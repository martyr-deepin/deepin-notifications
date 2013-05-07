#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Hou Shaohui
#
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
#             Wang Yaohua <mr.asianwang@gmail.com>
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
from ui.traypop import TrayPop
from dtk.ui.menu import Menu

from ui.window_view import BriefViewWindow, DetailViewWindow
from events import event_manager


class TrayIcon(gtk.StatusIcon):    
    
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.set_pixbuf_from_file("msg_white1.png")
        
        self.unread_items = []

        self.connect("button-press-event", self.on_button_press_event)
        event_manager.connect("show-unread", self.on_show_unread)
        
    def on_button_press_event(self, widget, event):
        if event.button == 1:
            event_manager.emit("show-unread", None)
            
    def set_pixbuf_from_file(self, file_name):
        self.pixbuf_file_name = file_name
        self.set_from_pixbuf(app_theme.get_pixbuf(self.pixbuf_file_name).get_pixbuf())
        
            
    def on_show_unread(self, data):
        '''
        docs
        '''                     
        TrayPop(1000, 500, self.unread_items).show_all()
        
        if self.pixbuf_file_name == "msg_white2.png":
            self.set_pixbuf_from_file("msg_white1.png")

trayicon = TrayIcon()
