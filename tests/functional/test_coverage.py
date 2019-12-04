""" Simple CLI functional tests.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click
from click.testing import CliRunner

import mitfixins


@click.command(
    cls=mitfixins.make_auto_config_command(
        version_text="Copyright 2019 Dave Rogers. Licensed under the GPLv3. "
                     "See LICENSE."
    ),
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@mitfixins.cli_verbose_option
@click.option("--foo", default="zzz")
@mitfixins.cli_dry_run_option
def main(**kwargs):
    """ Simplest possible mit-fixins CLI.
    """
    mitfixins.make_echo(mitfixins.Verbosity.LOW)(kwargs)


def test_coverage():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    result = runner.invoke(main, ["--print-config"])
    assert result.exit_code == 0
    result = runner.invoke(main, [])
    assert result.exit_code == 0


if __name__ == "__main__":  # pragma: no cover
    main()
