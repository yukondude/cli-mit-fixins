""" Utility function declarations.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import enum
import sys

import click

# noinspection PyProtectedMember
from click._compat import get_text_stderr as click_compat_get_text_stderr
from click.utils import echo as click_utils_echo


class Severity(enum.IntEnum):
    """ Possible message severities.
    """

    NORMAL = 1
    WARNING = 2
    ERROR = 3


class Verbosity(enum.IntEnum):
    """ Possible message levels of verbosity.
    """

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


def make_echo(verbosity: Verbosity):
    """ Return an echo function that displays or doesn't based on the verbosity count.
    """
    severity_ranks = {
        Severity.NORMAL: {"prefix": "", "style": {"bold": False}},
        Severity.WARNING: {
            "prefix": f"{Severity.WARNING.name} ",
            "style": {"fg": "yellow", "bold": True},
        },
        Severity.ERROR: {
            "prefix": f"{Severity.ERROR.name} ",
            "style": {"fg": "red", "bold": True},
        },
    }

    def echo_func(message, verbosity_threshold=Verbosity.LOW, severity=Severity.NORMAL):
        """ Display the message if the given threshold is no greater than the current
            verbosity count. Errors are always displayed. Warnings are displayed if the
            verbosity count is at least 1. Errors and warnings are sent to STDERR.
        """
        # Limit the threshold to at least low verbosity.
        verbosity_threshold = max(verbosity_threshold, Verbosity.LOW)

        if severity == Severity.WARNING:
            # Display warnings if verbosity is turned on at all.
            verbosity_threshold = Verbosity.LOW
        elif severity == Severity.ERROR:
            # Always display errors.
            verbosity_threshold = Verbosity.NONE

        if verbosity_threshold <= verbosity:
            severity_rank = severity_ranks.get(severity, severity_ranks[Severity.ERROR])
            prefix = severity_rank["prefix"]
            style = severity_rank["style"]

            is_err = severity != Severity.NORMAL
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

    make_echo(Verbosity.NONE)(self.format_message(), severity=3)
    sys.exit(1)


# Replace the usage error display function with show_usage().
click.exceptions.UsageError.show = _show_usage
