""" Functionally test the CLI test programs.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import re
import subprocess


def capture_command(args):
    here_path = os.path.dirname(os.path.realpath(__file__))
    command = [os.path.join(here_path, args[0])]
    command.extend(args[1:])
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode("utf-8"), err.decode("utf-8"), proc.returncode


def test_sorted_1():
    out, err, exit_code = capture_command(["cli_sorted_1.py", "--help"])
    assert exit_code == 0
    pattern = r"-a, --apple.+-B, --banana.+-h, --help.+-z, --zulu"
    assert re.search(pattern, out, re.DOTALL)
    assert not err


def test_sorted_2():
    out, err, exit_code = capture_command(["cli_sorted_2.py", "-h"])
    assert exit_code == 0
    pattern = r"-z, --zulu.+-B, --banana.+-a, --apple.+ -h, --help"
    assert re.search(pattern, out, re.DOTALL)
    assert not err


def test_versioned_1_help():
    out, err, exit_code = capture_command(["cli_versioned_1.py", "--help"])
    assert exit_code == 0
    pattern = r"-V, --version +Show the version number and exit."
    assert re.search(pattern, out, re.DOTALL)
    assert not err


def test_versioned_1_message():
    out, err, exit_code = capture_command(["cli_versioned_1.py", "--version"])
    assert exit_code == 0
    pattern = r"VERSION MESSAGE$"
    assert re.search(pattern, out, re.DOTALL)
    assert not err


def test_versioned_2():
    out, err, exit_code = capture_command(["cli_versioned_2.py", "-I"])
    assert exit_code == 0
    pattern = r"NUMBERINO MESSAGE$"
    assert re.search(pattern, out, re.DOTALL)
    assert not err


def test_versioned_2_fail():
    out, err, exit_code = capture_command(["cli_versioned_2.py", "--version"])
    assert exit_code != 0
    pattern = r"ERROR no such option: --version$"
    assert not out
    assert re.search(pattern, err, re.DOTALL)
