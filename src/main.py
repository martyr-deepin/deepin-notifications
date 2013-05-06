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
from events import event_manager
from ui.tray import trayicon
from ui.bubble import Bubble
from ui.utils import handle_message
from notification_db import db
from blacklist import blacklist

from collections import deque
from datetime import datetime


from ui.traypop import TrayPop

class DeepinNotification(object):
    def __init__(self):
        
        self.notification_queue = deque()

        self.mainloop_init()
        import dbus_notify
        self.dbus = dbus_notify.Notifications()
        
        event_manager.connect("notify", self.on_notify)
                
        import gtk
        gtk.main()
        
    def on_notify(self, data):
        '''
        docs
        '''
        message = handle_message(data) # replace hyper<a> with underline <u> AND place hyper actions in hints["x-deepin-hyperlinks"]
        height = 87 if len(message["actions"]) == 0 else 110
        create_time = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        
        if len(list(self.notification_queue)) > 0:
            event_manager.emit("ready-to-move-up", height)

        if message.app_name not in blacklist.bl:
            self.notification_queue.append(Bubble(message, height, create_time))
        db.add(create_time, message)
        trayicon.set_pixbuf_from_file("msg_white2.png")

        
    def mainloop_init(self):    
        import gobject
        gobject.threads_init()
        
        # dbus_init.
        import dbus, dbus.mainloop.glib
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        dbus.mainloop.glib.threads_init()
        dbus.mainloop.glib.gthreads_init()
        
        # gtk_init.
        import gtk
        gtk.gdk.threads_init()
    

if __name__ == "__main__":
    DeepinNotification()
   
