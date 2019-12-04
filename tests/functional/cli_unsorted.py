#!/usr/bin/env python3
""" Test unsorted help options.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click

import mitfixins


@click.command(
    cls=mitfixins.make_sorted_option_command(sort_help_options=False),
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("-z", "--zulu")
@click.option("-B", "--banana")
@click.option("-a", "--apple")
def main(**kwargs):
    """ Test unsorted help options.
    """
    mitfixins.make_echo(mitfixins.Verbosity.LOW)(kwargs)


if __name__ == "__main__":
    main()
