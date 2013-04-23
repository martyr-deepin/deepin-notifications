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
from dtk.ui.menu import Menu

from ui.window_view import brief_view_win
from events import event_manager


class TrayIcon(gtk.StatusIcon):    
    
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.set_pixbuf_from_file("msg_white1.png")
        self.menu = TrayMenu()
        self.connect("button-press-event", self.on_button_press_event)
        event_manager.connect("show-unread", self.on_show_unread)
        
    def get_menu_position(self):    
        return gtk.status_icon_position_menu(gtk.Menu(), self)
    
    def on_button_press_event(self, widget, event):
        if event.button == 1:
            event_manager.emit("show-unread", None)
        elif event.button == 3:
            print "show menu"
            (x, y, extra) = self.get_menu_position()
            self.menu.show((int(x), int(y)), (0, -32))
            
    def set_pixbuf_from_file(self, file_name):
        self.pixbuf_file_name = file_name
        self.set_from_pixbuf(app_theme.get_pixbuf(self.pixbuf_file_name).get_pixbuf())
        
            
    def on_show_unread(self, data):
        '''
        docs
        '''
        brief_view_win.show_all()
        if self.pixbuf_file_name == "msg_white2.png":
            self.set_pixbuf_from_file("msg_white1.png")
    
    

class TrayMenu(Menu):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        self.update_menu()
        Menu.__init__(self, self.menu_item, True)

    def update_menu(self):
        '''
        docs
        '''
        self.menu_item = []
        self.menu_item.append((None, "Show Unread", self.on_show_unread))
        self.menu_item.append((None, "Preference", self.on_show_preference))
        self.menu_item.append(None)
        self.menu_item.append((None, "No-Disturb", self.on_no_disturb_toggled))
        self.menu_item.append((None, "Normal Mode", self.on_normal_mode_toggled))
        
    def on_show_unread(self):
        '''
        docs
        '''
        event_manager.emit("show-unread", None)
    
    def on_show_preference(self):
        '''
        docs
        '''
        pass
    
    def on_no_disturb_toggled(self):
        '''
        docs
        '''
        pass
    
    def on_normal_mode_toggled(self):
        pass
    

trayicon = TrayIcon()
