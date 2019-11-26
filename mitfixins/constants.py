""" Constant declarations.
"""

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os

import click


COMMAND_NAME = os.path.splitext(__name__)[0]

DEFAULT_CONFIG_FILE_PATH = os.path.join(
    click.get_app_dir(app_name=COMMAND_NAME, force_posix=True), f"{COMMAND_NAME}.toml"
)

DEFAULT_CONFIG_FILE_OPTION = "config_file"

DEFAULT_PRINT_CONFIG_OPTION = "print_config"
