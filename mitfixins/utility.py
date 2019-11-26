""" Utility function declarations.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import sys

import click

# noinspection PyProtectedMember
from click._compat import get_text_stderr as click_compat_get_text_stderr
from click.utils import echo as click_utils_echo


def echo_wrapper(verbosity):
    """ Return an echo function that displays or doesn't based on the verbosity count.
    """
    severity_ranks = {
        1: {"prefix": "", "style": {"fg": "green", "bold": False}},
        2: {"prefix": "WARNING ", "style": {"fg": "yellow", "bold": True}},
        3: {"prefix": "ERROR ", "style": {"fg": "red", "bold": True}},
    }

    # Clamp the verbosity between 0 and 3.
    verbosity = min(max(verbosity, 0), 3)

    def echo_func(message, threshold=1, severity=1):
        """ Display the message if the given threshold is no greater than the current
            verbosity count. Errors are always displayed. Warnings are displayed if the
            verbosity count is at least 1. Errors and warnings are sent to STDERR.
        """
        # Clamp the threshold and severity between 1 and 3.
        threshold = min(max(threshold, 1), 3)
        severity = min(max(severity, 1), 3)

        if severity == 2:
            # Display warnings if verbosity is turned on at all.
            threshold = 1
        elif severity >= 3:
            # Always display errors.
            threshold = 0

        if threshold <= verbosity:
            severity_rank = severity_ranks.get(severity, severity_ranks[3])
            prefix = severity_rank["prefix"]
            style = severity_rank["style"]

            is_err = severity > 1
            click.secho(f"{prefix}{message}", err=is_err, **style)

    return echo_func


def _show_usage(self, file=None):
    """ Override the standard usage error message with a splash of colour.
        Taken from https://stackoverflow.com/a/43922088/726
    """
    if file is None:
        file = click_compat_get_text_stderr()

    if self.ctx is not None:
        color = self.ctx.color
        click_utils_echo(self.ctx.get_usage() + "\n", file=file, color=color)

    echo_wrapper(0)(self.format_message(), severity=3)
    sys.exit(1)


# Replace the usage error display function with show_usage().
click.exceptions.UsageError.show = _show_usage
