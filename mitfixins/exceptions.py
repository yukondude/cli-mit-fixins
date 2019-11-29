""" Exception declarations.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click

from .utility import make_echo


class CliException(click.ClickException):
    """ ClickException overridden to display errors using echo_wrapper()'s formatting.
    """

    def show(self, file=None):  # pragma no cover
        """ Display the error.
        """
        _ = file
        make_echo(0)(self.format_message(), severity=3)
