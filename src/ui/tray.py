#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Hou Shaohui
#
# Author:     Hou Shaohui <houshao55@gmail.com>
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

import gtk
from ui.skin import app_theme

class TrayIcon(gtk.StatusIcon):    
    
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.set_from_pixbuf(app_theme.get_pixbuf("skin/logo.ico").get_pixbuf())
        self.set_visible(True)
        
    def get_menu_position(self, menu, icon):    
        return gtk.status_icon_position_menu(menu, icon)
