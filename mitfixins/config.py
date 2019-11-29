""" CLI helper functions.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import pathlib
import sys

import click
import toml

from .constants import COMMAND_NAME
from .exceptions import CliException
from .utility import make_echo, Verbosity


DEFAULT_CONFIG_FILE_PATH = os.path.join(
    click.get_app_dir(app_name=COMMAND_NAME, force_posix=True), f"{COMMAND_NAME}.toml"
)

DEFAULT_CONFIG_FILE_OPTION_NAME = "config_file"

DEFAULT_PRINT_CONFIG_OPTION_NAME = "print_config"
DEFAULT_PRINT_CONFIG_OPTION_SWITCHES = ("--print-config",)
DEFAULT_PRINT_CONFIG_OPTION_HELP = (
    "Print a sample configuration file that corresponds to the command line options "
    "and exit. Ignores the settings from a configuration file. This must be the final "
    "option switch for the command."
)


class AutoConfigCommand(click.Command):
    """ Click Command subclass that loads settings from a configuration file.
    """

    config_file_option_name = None
    print_config_option_name = None
    print_config_option_switches = None
    print_config_option_help = None
    print_config_callback = None
    sort_help_options = False

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

        params = params or []
        params.append(print_config_option)

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

    def format_options(self, ctx, formatter):
        """ Override Click's default listing of options, sorting them if necessary.
        """

        def switch_sort_key(element):
            """ Extract the names of the option switches without leading hyphens.
            """
            switches = element[0].lower()
            switch_list = [s.strip().strip("-") for s in switches.split(",")]
            return "|".join(switch_list)

        opts = []

        for param in self.get_params(ctx):
            switch_help = param.get_help_record(ctx)

            if switch_help is not None:
                opts.append(switch_help)

        if opts:
            if self.sort_help_options:
                opts.sort(key=switch_sort_key)

            with formatter.section("Options"):
                formatter.write_dl(opts)

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
            config_path = ctx.params[self.config_file_option_name]

            if not config_path:
                config_path = DEFAULT_CONFIG_FILE_PATH

            if pathlib.Path(config_path).exists():
                settings = self.load_toml_config(config_path)
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
    def load_toml_config(config_path):
        """ Load the settings from the given path to a TOML-format configuration file.
        """
        settings = {}

        with open(config_path, "r") as config_file:
            try:
                settings = toml.load(config_file)[COMMAND_NAME]
            except toml.TomlDecodeError as exc:
                raise CliException(
                    f"Unable to parse configuration file '{config_path}': {exc}"
                )

        return settings

    @staticmethod
    def print_config(options, excluded_options, arguments, render_func):
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

        return render_func(settings, arguments)

    @staticmethod
    def render_toml_config(settings, arguments):
        """ Return the settings rendered into a TOML-format configuration file string.
        """
        lines = [
            f"# Sample {COMMAND_NAME} configuration file, by default located at "
            f"{DEFAULT_CONFIG_FILE_PATH}.",
            "# Configuration options already set to the default value are "
            "commented-out.",
            "",
            f"[{COMMAND_NAME}]",
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


def make_auto_config_command(
    config_file_option_name=DEFAULT_CONFIG_FILE_OPTION_NAME,
    print_config_option_name=DEFAULT_PRINT_CONFIG_OPTION_NAME,
    print_config_option_switches=DEFAULT_PRINT_CONFIG_OPTION_SWITCHES,
    print_config_option_help=DEFAULT_PRINT_CONFIG_OPTION_HELP,
    sort_help_options=True,
    excluded_options=None,
):
    """ Return a custom Command class that loads any configuration file before
        arguments passed on the command line.
        Based on https://stackoverflow.com/a/46391887/726
    """
    excluded_options = excluded_options if excluded_options is not None else []
    excluded_options.extend([config_file_option_name, print_config_option_name])

    def print_config_callback(ctx, param, value):
        """ Print the sample configuration file, delegating the real work to
            print_config().
        """
        _ = param

        if not value or ctx.resilient_parsing:
            return

        config = AutoConfigCommand.print_config(
            ctx.command.params,
            excluded_options,
            ctx.params,
            AutoConfigCommand.render_toml_config,
        )
        make_echo(Verbosity.HIGH)(config)
        ctx.exit()

    command_class = AutoConfigCommand
    command_class.config_file_option_name = config_file_option_name
    command_class.print_config_option_name = print_config_option_name
    command_class.print_config_option_switches = print_config_option_switches
    command_class.print_config_option_help = print_config_option_help
    command_class.print_config_callback = print_config_callback
    command_class.sort_help_options = sort_help_options
    return command_class
