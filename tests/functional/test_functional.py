""" Functionally test the CLI test programs.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import re
import subprocess


HERE_PATH = os.path.dirname(os.path.realpath(__file__))


def capture(args):
    command = [os.path.join(HERE_PATH, args[0])]
    command.extend(args[1:])
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode("utf-8"), err.decode("utf-8"), proc.returncode


def test_sorted():
    out, err, exit_code = capture(["cli_sorted.py", "--help"])
    assert exit_code == 0
    pattern = r"-a, --apple.+-B, --banana.+-h, --help.+-z, --zulu"
    assert re.search(pattern, out, re.DOTALL)
    assert not err


def test_unsorted():
    out, err, exit_code = capture(["cli_unsorted.py", "--help"])
    assert exit_code == 0
    pattern = r"-z, --zulu.+-B, --banana.+-a, --apple.+ -h, --help"
    assert re.search(pattern, out, re.DOTALL)
    assert not err
