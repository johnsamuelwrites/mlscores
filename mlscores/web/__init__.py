#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Web interface module for mlscores."""

from .app import app, run_server

__all__ = ["app", "run_server"]
