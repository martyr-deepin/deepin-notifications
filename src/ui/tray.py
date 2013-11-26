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

from datetime import datetime, timedelta, time

import gtk
from ui.skin import app_theme
from traypop import TrayPop
from events import event_manager
from unread_db import unread_db
from window_view import DetailWindow

ID = 0
TIME = 1
MESSAGE = 2


class TrayIcon(gtk.StatusIcon):    
    
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.set_pixbuf_from_file("msg_white1.png")
        self.detail_window = DetailWindow()
        
        self.connect("button-press-event", self.on_button_press_event)
        event_manager.connect("listview-items-added", self.on_traypop_listview_items_added)
        
    def on_button_press_event(self, widget, event):
        if event.button == 1:
            self.show_unread()
            
    def set_pixbuf_from_file(self, file_name):
        self.pixbuf_file_name = file_name
        self.set_from_pixbuf(app_theme.get_pixbuf(self.pixbuf_file_name).get_pixbuf())
        
        
    def generate_traypop_position(self):
        x, y, not_important = gtk.status_icon_position_menu(gtk.Menu(), self)
        
        return x + 7, y - 20
    
    def on_notify_receive(self, data):
        self.increase_unread(data)
        
        if self.detail_window.is_empty:
            self.detail_window.refresh_view()
        else:
            self.detail_window.add_to_view()
    
    def increase_unread(self, data):
        self.check_date_for_db_clean_up()
        self.unread_items = data
        
    def check_date_for_db_clean_up(self):
        now = datetime.now()
        today = now.date()
        today_0 = datetime.combine(today, time(0, 0, 0))
        today_4 = datetime.combine(today, time(4, 0, 0))
        
        if not today_0 > now > today_4:
            if not unread_db.cleaned_up:
                unread_db.clear_date(today_0)
        
    def on_traypop_listview_items_added(self, items):
        for item in items:
            unread_db.remove(item.id)
        unread_db.commit()
            
    def show_unread(self):
        '''
        docs
        '''                     
        x, y = self.generate_traypop_position()
        
        TrayPop(self).show_up()
        
        if self.pixbuf_file_name == "msg_white2.png":
            self.set_pixbuf_from_file("msg_white1.png")
            
            
    def unread_items():
        doc = "easy way to manage unread_items, like a variable"
        
        def fget(self):
            db_all =  unread_db.get_all()
            results = []
            for item in db_all:
                item_datetime = datetime.strptime(item[TIME], "%Y/%m/%d-%H:%M:%S")                
                if datetime.today() - item_datetime < timedelta(days=1):
                    results.append(item)
                    
            return results
        
        def fset(self, new_item):
            create_time = new_item[0]
            notification = new_item[1]
            
            unread_db.add(create_time, notification)
            self.set_pixbuf_from_file("msg_white2.png")
                
        return locals()
        
    unread_items = property(**unread_items())
        
            
trayicon = TrayIcon()
