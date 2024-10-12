#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
import os

# Add the parent directory (project root) to sys.path so that pytest can find my_package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
