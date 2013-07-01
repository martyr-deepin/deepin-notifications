#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou ShaoHui
# 
# Author:     Hou ShaoHui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from dtk.ui.init_skin import init_skin
from deepin_utils.file import get_parent_dir
from dtk.ui.skin_config import skin_config
import os

PROGRAM_NAME = "deepin-notifications" 
PROGRAM_VERSION = "1.0"

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

app_theme = init_skin(
    PROGRAM_NAME,
    PROGRAM_VERSION,
    "blue",
    os.path.join(get_parent_dir(__file__, 3), "skin"),
    os.path.join(get_parent_dir(__file__, 3), "app_theme"),
    )

skin_config.set_application_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
