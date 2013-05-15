#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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
from collections import deque
from datetime import datetime

from events import event_manager
from ui.tray import trayicon
from ui.bubble import Bubble
from ui.utils import handle_notification
from notification_db import db
from blacklist import blacklist
from preference import preference
from unread_db import unread_db
from spec import Server


class DeepinNotification(object):
    def __init__(self):
        
        self.server = Server()
        self.notification_queue = deque()

        self.server.connect('show-notification', self.on_show_notification)
        event_manager.connect("manual-cancelled", self.on_dismiss_notification)
        event_manager.connect("expire-completed", self.on_expire_notification)
        
        self.mainloop_init()
        
    def on_dismiss_notification(self, bubble):
        self.server.dismiss(bubble.notification)
        
        if bubble in self.notification_queue:
            self.notification_queue.remove(bubble)
        
    def on_expire_notification(self, bubble):
        self.server.expire(bubble.notification)
        
        if bubble in self.notification_queue:
            self.notification_queue.remove(bubble)
        
        
    def on_show_notification(self, server, notification):
        '''
        docs
        '''
         # replace hyper<a> with underline <u> AND place hyper actions in hints["x-deepin-hyperlinks"]
        notification = handle_notification(notification)
        height = 87 if len(notification.actions) == 0 else 110
        create_time = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        
        if len(list(self.notification_queue)) > 0:
            event_manager.emit("ready-to-move-up", height)

        if not preference.disable_bubble:
            if notification.app_name not in blacklist.bl:
                self.notification_queue.append(Bubble(notification, height, create_time))
                if len(self.notification_queue) > 3:
                    self.notification_queue.pop()
                    
        trayicon.set_pixbuf_from_file("msg_white2.png")                
        db.add(create_time, notification)

        
    def mainloop_init(self):    
        import gobject
        gobject.threads_init()
        
        # dbus_init.
        import dbus.mainloop.glib
        dbus.mainloop.glib.threads_init()
        dbus.mainloop.glib.gthreads_init()
        
        # gtk_init.
        import gtk
        gtk.gdk.threads_init()
        gtk.main()
    

if __name__ == "__main__":
    DeepinNotification()
   
