""" CLI helper function unit tests.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

from click.core import Option
from click.testing import CliRunner
import pytest

from mitfixins.config import AutoConfigCommand, DEFAULT_CONFIG_FILE_PATH
from mitfixins.constants import COMMAND_NAME
from mitfixins.exceptions import CliException


@pytest.mark.parametrize("options,expected", [
    # options,                                                expected
    ((Option(["--apple"]),),                                  ""),
    ((Option(["--apple", "-a"]),),                            "a"),
    ((Option(["--apple", "-a"]), Option(["--banana", "-B"])), "aB"),
])
def test_get_short_switches(options, expected):
    assert AutoConfigCommand.get_short_switches(options) == expected


@pytest.mark.parametrize("switches,short_switches,arguments,expected", [
    # switches,         short_switches, arguments,                    expected
    (("-a", "--apple"), "aBcD",         ("",),                        False),
    (("-a", "--apple"), "aBcD",         ("--banana",),                False),
    (("-a", "--apple"), "aBcD",         ("-a",),                      True),
    (("-a", "--apple"), "aBcD",         ("--apple",),                 True),
    (("-a", "--apple"), "aBcD",         ("-BcDaqux",),                True),
    (("-a", "--apple"), "aBcD",         ("-BcEaqux",),                False),
    (("-p", "--apple"), "aBcD",         ("apple",),                   False),
    (("-p", "--apple"), "aBcD",         ("-apple",),                  False),
    (("-p", "--apple"), "aBcD",         ("---apple",),                False),
    (("-p", "--apple"), "aBcD",         ("p",),                       False),
    (("-p", "--apple"), "aBcD",         ("--p",),                     False),
    (("-a", "--apple"), "aBcD",         ("-D", "--banana", "-a"),     True),
    (("-a", "--apple"), "aBcD",         ("-D", "--apple", "food"),    True),
    (("-a", "--apple"), "aBcD",         ("-D", "--apple=food", "-a"), True),
])
def test_is_option_switch_in_arguments(switches, short_switches, arguments, expected):
    assert AutoConfigCommand.is_option_switch_in_arguments(
        switches,
        short_switches,
        arguments
    ) == expected


@pytest.mark.parametrize("element,expected", [
    # element,      #expected
    ([""],                        ""),
    (["-a"],                      "a"),
    (["-A"],                      "a"),
    (["--a"],                     "a"),
    (["--A"],                     "a"),
    (["-a, --banana"],            "abanana"),
    (["--a, -b"],                 "ab"),
    (["--a, --banana"],           "abanana"),
    (["--apple , --banana"],      "applebanana"),
    (["--apple,-b"],              "appleb"),
    (["--a, "],                   "a"),
    ([",-b"],                     "b"),
    ([" , --banana"],             "banana"),
    (["-a, --banana , --cherry"], "abananacherry"),
])
def test_get_switch_sort_key(element, expected):
    assert AutoConfigCommand.get_switch_sort_key(element) == expected


def test_load_toml_config_fail():
    with CliRunner().isolated_filesystem():
        with open('test.toml', 'w') as toml_file:
            toml_file.write("BAD MOJO")

        with pytest.raises(CliException):
            assert AutoConfigCommand.load_toml_config("test.toml")


def test_load_toml_config_pass():
    with CliRunner().isolated_filesystem():
        with open('test.toml', 'w') as toml_file:
            toml_file.write(f"[{COMMAND_NAME}]\nvariable = 13")

        assert {"variable": 13} == AutoConfigCommand.load_toml_config("test.toml")


@pytest.mark.parametrize("options,excluded_options,arguments,expected", [
    # options, excluded_options, arguments, expected
    ([], [], {}, ""),
    ([Option(["--apple"])], [], {"apple": 42}, "apple:42"),
    ([Option(["--apple"]), Option(["--banana"])], [], {"banana": 13, "apple": 42},
     "apple:42,banana:13"),
    ([Option(["--apple"]), Option(["--banana"])], ["banana"],
     {"banana": 13, "apple": 42}, "apple:42"),
    ([Option(["--apple"], is_eager=True), Option(["--banana"])], [],
     {"banana": 13, "apple": 42}, "banana:13"),
])
def test_print_config(options, excluded_options, arguments, expected):
    def mock_render(settings, arguments_):
        _ = arguments
        return ",".join([f"{s}:{arguments_[s]}" for s in sorted(settings)])

    assert AutoConfigCommand.print_config(
        options,
        excluded_options,
        arguments,
        mock_render
    ) == expected


EXPECTED_EMPTY_CONFIG = f"""# Sample {COMMAND_NAME} configuration file, by """ + \
    f"""default located at {DEFAULT_CONFIG_FILE_PATH}.
# Configuration options already set to the default value are commented-out.

[{COMMAND_NAME}]"""

EXPECTED_DEFAULT_CONFIG = EXPECTED_EMPTY_CONFIG + f"""

# This is a setting
# a = 13"""

EXPECTED_NONDEFAULT_CONFIG = EXPECTED_EMPTY_CONFIG + f"""

# This is a setting
a = 33"""


@pytest.mark.parametrize("settings,arguments,expected", [
    # settings,                                                   arguments,
    # expected
    ({},                                                          {},
     EXPECTED_EMPTY_CONFIG),
    ({"a": Option(["-a"], default=13, help="This is a setting")}, {"a": 13},
     EXPECTED_DEFAULT_CONFIG),
    ({"a": Option(["-a"], default=13, help="This is a setting")}, {"a": 33},
     EXPECTED_NONDEFAULT_CONFIG),
])
def test_render_toml_config(settings, arguments, expected):
    assert AutoConfigCommand.render_toml_config(settings, arguments) == expected
