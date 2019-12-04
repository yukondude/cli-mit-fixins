""" CLI helper functions.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import pathlib
import sys

import pkg_resources

import click
import toml

from .exceptions import CliException
from .utility import make_echo, Verbosity


DEFAULT_CONFIG_FILE_OPTION_NAME = "config_file"

DEFAULT_PRINT_CONFIG_OPTION_NAME = "print_config"
DEFAULT_PRINT_CONFIG_OPTION_SWITCHES = ("--print-config",)
DEFAULT_PRINT_CONFIG_OPTION_HELP = (
    "Print a sample configuration file that corresponds to the command line options "
    "and exit. Ignores the settings from a configuration file. This must be the final "
    "option switch for the command."
)

DEFAULT_VERSION_OPTION_SWITCHES = ("-V", "--version")
DEFAULT_VERSION_OPTION_HELP = "Show the version number and exit."


class SortedOptionCommand(click.Command):
    """ Click Command subclass that can sort the options if desired.
    """

    sort_help_options = False

    def format_options(self, ctx, formatter):
        """ Override Click's default listing of options, sorting them if necessary.
        """
        opts = []

        for param in self.get_params(ctx):
            switch_help = param.get_help_record(ctx)

            if any(switch_help):
                opts.append(switch_help)

        if opts:
            if self.sort_help_options:
                opts.sort(key=self.get_switch_sort_key)

            with formatter.section("Options"):
                formatter.write_dl(opts)

    @staticmethod
    def get_switch_sort_key(element):
        """ Extract the concatenated names of the option switches without leading
            hyphens.
        """
        return "".join([s.strip().strip("-") for s in element[0].lower().split(",")])


class VersionedCommand(SortedOptionCommand):
    """ Click Command subclass that supports a version option and can sort the options
        if desired.
    """

    version_option_switches = None
    version_option_help = None
    version_option_callback = None

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        name,
        context_settings=None,
        callback=None,
        params=None,
        help=None,
        epilog=None,
        short_help=None,
        options_metavar="[OPTIONS]",
        add_help_option=True,
        hidden=False,
        deprecated=False,
    ):

        version_option = click.Option(
            self.version_option_switches,
            is_flag=True,
            callback=self.__class__.version_option_callback,
            expose_value=False,
            is_eager=True,
            help=self.version_option_help,
        )

        params = params or []
        params.append(version_option)

        super().__init__(
            name,
            context_settings,
            callback,
            params,
            help,
            epilog,
            short_help,
            options_metavar,
            add_help_option,
            hidden,
            deprecated,
        )


class AutoConfigCommand(VersionedCommand):
    """ Click Command subclass that loads settings from a configuration file and that
        can emit configuration file settings from the given command line arguments,
        supports a version option, and can sort the options if desired.
    """

    config_file_option_name = None
    print_config_option_name = None
    print_config_option_switches = None
    print_config_option_help = None
    print_config_callback = None

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        name,
        context_settings=None,
        callback=None,
        params=None,
        help=None,
        epilog=None,
        short_help=None,
        options_metavar="[OPTIONS]",
        add_help_option=True,
        hidden=False,
        deprecated=False,
    ):

        print_config_option = click.Option(
            self.print_config_option_switches,
            is_flag=True,
            callback=self.__class__.print_config_callback,
            expose_value=False,
            help=self.print_config_option_help,
        )
        config_file_option = click.Option(
            ["--config-file", "-C"],
            type=click.Path(
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
            help="Full path of a TOML-format configuration file.",
        )

        params = params or []
        params.extend((print_config_option, config_file_option))

        super().__init__(
            name,
            context_settings,
            callback,
            params,
            help,
            epilog,
            short_help,
            options_metavar,
            add_help_option,
            hidden,
            deprecated,
        )

    @staticmethod
    def get_config_path(command_name, config_path_override):
        """ Return the configuration file path for the given command name and overriding
            file path, if specified.
        """
        if config_path_override:
            return config_path_override

        config_slug = AutoConfigCommand.get_config_slug(command_name)

        return os.path.join(
            click.get_app_dir(app_name=config_slug, force_posix=True),
            f"{config_slug}.toml",
        )

    @staticmethod
    def get_config_slug(command_name):
        """ Return a legal TOML section name slug from the given command name.
        """
        return os.path.splitext(command_name)[0].lower().replace(".", "-").strip("-")

    @staticmethod
    def get_short_switches(options):
        """ Return a string of gathered 'short' (1 character) option switches.
        """
        short_switch_list = []

        for option in options:
            if isinstance(option, click.core.Option):
                for switch in option.opts + option.secondary_opts:
                    if switch.startswith("-") and len(switch) == 2:
                        short_switch_list.append(switch[1])

        return "".join(short_switch_list)

    def invoke(self, ctx):
        """ Load the configuration settings into the context.
        """
        if self.config_file_option_name in ctx.params:
            command_name = ctx.command_path
            config_path = self.get_config_path(
                command_name, ctx.params[self.config_file_option_name]
            )

            if pathlib.Path(config_path).exists():
                settings = self.load_toml_config(command_name, config_path)
                short_switches = self.get_short_switches(ctx.command.params)

                for option in ctx.command.params:
                    if option.name not in ctx.params or not isinstance(
                        option, click.core.Option
                    ):
                        continue

                    # Third preferential choice for option value is the declared
                    # default. Second choice is the configuration file setting.
                    value = settings.get(option.name, option.default)

                    # ...and first choice is the value passed on the command line.
                    # Have to check this manually because the context already
                    # includes the default if the option wasn't specified. Click
                    # doesn't seem to report if a value arrived via the default or
                    # explicitly on the command line and I haven't figured a way to
                    # intercept the normal parsing to implement this myself.
                    if self.is_option_switch_in_arguments(
                        option.opts + option.secondary_opts,
                        short_switches,
                        sys.argv[1:],
                    ):
                        value = ctx.params[option.name]

                    ctx.params[option.name] = value

        return super().invoke(ctx)

    @staticmethod
    def is_option_switch_in_arguments(switches, short_switches, arguments):
        """ Return True if the given option switches appear on the command line. This
            is, admittedly, a bit of a hackish re-implementation of the Click argument
            parser.
        """
        for argument in [a for a in arguments if a.startswith("-")]:
            for switch in switches:
                if argument.startswith(switch):
                    # Long switches
                    return True

                if len(switch) == 2 and len(argument) >= 2 and argument[1] != "-":
                    # Short switches
                    for char in argument[1:]:
                        if char not in short_switches:
                            # Hit a character that's not one of the recognized short
                            # switches so it must be part of an argument value.
                            break

                        if char == switch[1]:
                            return True

        return False

    @staticmethod
    def load_toml_config(command_name, config_path):
        """ Load the settings from the given path to a TOML-format configuration file.
        """
        settings = {}
        config_slug = AutoConfigCommand.get_config_slug(command_name)

        with open(config_path, "r") as config_file:
            try:
                settings = toml.load(config_file)[config_slug]
            except KeyError:
                raise CliException(
                    f"Unable to parse [{config_slug}] section from '{config_path}'."
                )
            except toml.TomlDecodeError as exc:
                raise CliException(
                    f"Unable to parse configuration file '{config_path}': {exc}"
                )

        return settings

    @staticmethod
    def print_config(
        command_name, config_path, options, excluded_options, arguments, render_func
    ):
        """ Return the sample configuration file for the defined options and command
            line arguments via the given render function as a string.
        """
        settings = {}

        for option in options:
            if (
                isinstance(option, click.core.Option)
                and not option.is_eager
                and option.name not in excluded_options
            ):
                settings[option.name] = option

        return render_func(command_name, config_path, settings, arguments)

    @staticmethod
    def render_toml_config(command_name, config_path, settings, arguments):
        """ Return the settings rendered into a TOML-format configuration file string.
        """
        config_slug = AutoConfigCommand.get_config_slug(command_name)
        lines = [
            f"# Sample {command_name} configuration file, by default located at "
            f"{config_path}.",
            "# Configuration options already set to the default value are "
            "commented-out.",
            "",
            f"[{config_slug}]",
            "",
        ]

        for setting_name in sorted(settings):
            setting = settings[setting_name]
            argument = arguments.get(setting_name)

            if argument is not None and argument != ():
                if setting.help:
                    lines.append(f"# {setting.help}")

                prefix = "# " if argument == setting.default else ""
                toml_setting = toml.dumps({setting_name: argument})
                lines.append(f"{prefix}{toml_setting}")

        return "\n".join(lines).strip()


def make_sorted_option_command(sort_help_options=True):
    """ Return a custom Command subclass that can sort the options if desired.
    """
    command_class = AutoConfigCommand
    command_class.sort_help_options = sort_help_options
    return command_class


def make_versioned_command(
    version_option_switches=DEFAULT_VERSION_OPTION_SWITCHES,
    version_option_help=DEFAULT_VERSION_OPTION_HELP,
    version_text="",
    sort_help_options=True,
):
    """ Return a custom Command subclass that supports a version option and can sort the
        options if desired.
        Based on https://stackoverflow.com/a/46391887/726
    """

    def version_option_callback(ctx, echo):
        """ Show the version number and exit.
        """
        try:
            version = pkg_resources.get_distribution(ctx.command_path).version
            echo(f"{ctx.command_path} version {version}")
        except pkg_resources.DistributionNotFound:  # pragma: no cover
            echo(f"{ctx.command_path} (version not registered)")

        if version_text:
            echo(version_text)

    command_class = make_sorted_option_command(sort_help_options)
    command_class.version_option_switches = version_option_switches
    command_class.version_option_help = version_option_help
    command_class.version_option_callback = make_eager_callback(version_option_callback)
    return command_class


def make_auto_config_command(
    config_file_option_name=DEFAULT_CONFIG_FILE_OPTION_NAME,
    print_config_option_name=DEFAULT_PRINT_CONFIG_OPTION_NAME,
    print_config_option_switches=DEFAULT_PRINT_CONFIG_OPTION_SWITCHES,
    print_config_option_help=DEFAULT_PRINT_CONFIG_OPTION_HELP,
    version_option_switches=DEFAULT_VERSION_OPTION_SWITCHES,
    version_option_help=DEFAULT_VERSION_OPTION_HELP,
    version_text="",
    sort_help_options=True,
    excluded_options=None,
):
    """ Return a custom Command subclass that loads settings from a configuration file
        and that can emit configuration file settings from the given command line
        arguments, supports a version option, and can sort the options if desired.
        Based on https://stackoverflow.com/a/46391887/726
    """
    excluded_options = excluded_options if excluded_options is not None else []
    excluded_options.extend([config_file_option_name, print_config_option_name])

    def print_config_callback(ctx, echo):
        """ Print the sample configuration file, delegating the real work to
            print_config().
        """
        config = AutoConfigCommand.print_config(
            ctx.command_path,
            AutoConfigCommand.get_config_path(
                ctx.command_path, ctx.params.get(config_file_option_name)
            ),
            ctx.command.params,
            excluded_options,
            ctx.params,
            AutoConfigCommand.render_toml_config,
        )
        echo(config)

    command_class = make_versioned_command(
        version_option_switches, version_option_help, version_text, sort_help_options
    )
    command_class.config_file_option_name = config_file_option_name
    command_class.print_config_option_name = print_config_option_name
    command_class.print_config_option_switches = print_config_option_switches
    command_class.print_config_option_help = print_config_option_help
    command_class.print_config_callback = make_eager_callback(print_config_callback)
    command_class.sort_help_options = sort_help_options
    return command_class


def make_eager_callback(wrapped_func):
    """ Return an eager Click parameter callback function that delegates emitting output
        to the given wrapped function.
    """

    def eager_callback(ctx, param, value):
        """ Call the wrapped function and exit immediately.
        """
        if not value or ctx.resilient_parsing:
            return

        wrapped_func(ctx, echo=make_echo(Verbosity.HIGH))
        ctx.exit()
        _ = param

    return eager_callback
