#!/usr/bin/env python3
""" Test version option, variant #2.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click

import mitfixins


@click.command(
    cls=mitfixins.make_versioned_command(
        version_option_help="What version be you?",
        version_option_switches=["-I", "--numberino"],
        version_text="NUMBERINO MESSAGE",
    ),
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def main(**kwargs):
    """ Test version option, variant #2.
    """
    mitfixins.make_echo(mitfixins.Verbosity.LOW)(kwargs)


if __name__ == "__main__":
    main()
