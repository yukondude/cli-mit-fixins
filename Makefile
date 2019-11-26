# cli-mit-fixins command Makefile for various and sundry project tasks.

# This file is part of cli-mit-fixins.
# Copyright Dave Rogers 2019 <thedude@yukondyde.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

.SILENT: help test fulltest

help:
	echo "MAKE TARGETS"
	echo "test      Run all tests and show coverage."
	echo "fulltest  Run all tests (verbose), show coverage, and code analyses."

test:
	coverage run --module py.test
	coverage report --show-missing --omit='*site-packages*,*__init__.py'

fulltest:
	coverage run --module py.test --verbose
	echo
	echo "Coverage Statistics"
	-coverage report --fail-under 80 --show-missing --omit='*site-packages*,*__init__.py'
	echo
	echo "Radon Cyclomatic Complexity (CC)"
	radon cc --average cli-mit-fixins
	echo
	echo "Radon Maintainability Index (MI)"
	radon mi --show --sort cli-mit-fixins
