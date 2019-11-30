""" Decorator declarations.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click


def cli_config_file_option(func):
    """ Decorator to enable the --config-file/-C option.
    """
    return click.option(
        "--config-file",
        "-C",
        type=click.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
        help="Full path of the TOML-format configuration file.",
    )(func)


def cli_dry_run_option(func):
    """ Decorator to enable the --dry-run/-D option.
    """
    return click.option(
        "--dry-run",
        "-D",
        is_flag=True,
        help="Show the intended operations but do not run them (implies --verbose).",
    )(func)


def cli_print_config_option(func):
    """ Decorator to enable the --print-config option.
    """
    return click.option(
        "--print-config",
        is_flag=True,
        help="Print a sample configuration file that corresponds to the command "
        "line options and exit. Ignores the settings from a configuration file.",
    )(func)


def cli_verbose_option(func):
    """ Decorator to enable the --verbose/-v option.
    """
    return click.option(
        "--verbose",
        "-v",
        count=True,
        help="Increase the verbosity of status messages: use once for normal output, "
        "twice for additional output, and thrice for debug-level output.",
    )(func)
