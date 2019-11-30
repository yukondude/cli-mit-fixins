""" Decorator unit tests.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

# from mitfixins.decorators import show_version
#
#
# def test_show_version_fail(capsys):
#     show_version(None, None, None)
#     captured_out, captured_err = capsys.readouterr()
#     assert captured_out == ""
#     assert captured_err == ""


# def test_show_version(capsys, version_message):
#     class MockContext:
#         resilient_parsing = False
#
#         def exit(self):
#             pass
#
#     show_version(MockContext(), None, True)
#     captured_out, captured_err = capsys.readouterr()
#     assert captured_out == version_message
#     assert captured_err == ""
