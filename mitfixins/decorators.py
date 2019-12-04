""" Decorator declarations.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click


def cli_dry_run_option(func):
    """ Decorator to enable the --dry-run/-D option.
    """
    return click.option(
        "--dry-run",
        "-D",
        is_flag=True,
        help="Show the intended operations but do not run them (implies --verbose).",
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
