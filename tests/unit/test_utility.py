""" Utility function unit tests.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import pytest

from mitfixins.utility import make_echo, Verbosity, Severity


@pytest.mark.parametrize("arguments,expected", [
    # verbosity, threshold, severity, message:   stdout,  stderr
    ((0,         1,         1,        "info"),  ("",      "")),
    ((1,         1,         1,        "info"),  ("info",  "")),
    ((2,         1,         1,        "info"),  ("info",  "")),
    ((3,         1,         1,        "info"),  ("info",  "")),
    ((0,         1,         2,        "warn"),  ("",      "")),
    ((1,         1,         2,        "warn"),  ("",      "WARNING warn")),
    ((2,         1,         2,        "warn"),  ("",      "WARNING warn")),
    ((3,         1,         2,        "warn"),  ("",      "WARNING warn")),
    ((0,         1,         3,        "error"), ("",      "ERROR error")),
    ((1,         1,         3,        "error"), ("",      "ERROR error")),
    ((2,         1,         3,        "error"), ("",      "ERROR error")),
    ((3,         1,         3,        "error"), ("",      "ERROR error")),
    ((0,         0,         1,        "info"),  ("",      "")),
    ((0,         1,         1,        "info"),  ("",      "")),
    ((0,         2,         1,        "more"),  ("",      "")),
    ((0,         3,         1,        "debug"), ("",      "")),
    ((1,         0,         1,        "info"),  ("info",  "")),
    ((1,         1,         1,        "info"),  ("info",  "")),
    ((1,         2,         1,        "more"),  ("",      "")),
    ((1,         3,         1,        "debug"), ("",      "")),
    ((2,         0,         1,        "info"),  ("info",  "")),
    ((2,         1,         1,        "info"),  ("info",  "")),
    ((2,         2,         1,        "more"),  ("more",  "")),
    ((2,         3,         1,        "debug"), ("",      "")),
    ((3,         0,         1,        "info"),  ("info",  "")),
    ((3,         1,         1,        "info"),  ("info",  "")),
    ((3,         2,         1,        "more"),  ("more",  "")),
    ((3,         3,         1,        "debug"), ("debug", "")),
])
def test_echo_wrapper(capsys, arguments, expected):
    verbosity, threshold, severity, message = arguments
    expected_out, expected_err = expected

    echo = make_echo(Verbosity(verbosity))
    echo(message, Verbosity(threshold), Severity(severity))

    captured_out, captured_err = capsys.readouterr()
    assert captured_out.strip() == expected_out
    assert captured_err.strip() == expected_err
