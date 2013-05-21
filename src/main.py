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
from ui.utils import handle_notification
from notification_db import db
from blacklist import blacklist
from preference import preference

from collections import deque
from datetime import datetime


class DeepinNotification(object):
    def __init__(self):
        
        self.mainloop_init()
        
        import dbus_notify
        self.dbus = dbus_notify.Notifications()
        
        self.notification_queue = deque() # queue to store bubbles
        self.notify_queue = deque() # record the number of unnotified notifies.
        
        event_manager.connect("notify", self.on_notify)
        event_manager.connect("bubble-animation-done", self.on_bubble_animation_done)
        
        import gtk
        gtk.main()
                
        
    def on_notify(self, notification):
        '''
        docs
        '''
         # replace hyper<a> with underline <u> AND place hyper actions in hints["x-deepin-hyperlinks"]
        message = handle_notification(notification)
        
        height = 87 if len(message["actions"]) == 0 else 110
        create_time = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        
        bubble = None
        
        if not preference.disable_bubble:
            if message.app_name not in blacklist.bl:
                if len(self.notification_queue) != 0:
                    for notification in self.notification_queue:
                        if notification.fade_in_moving or notification.move_up_moving:
                            self.notify_queue.appendleft((message, height, create_time))
                        else:
                            event_manager.emit("ready-to-move-up", height)                            
                            bubble = Bubble(message, height, create_time)
                else:
                    bubble = Bubble(message, height, create_time)

                if bubble:
                        self.notification_queue.append(bubble)
                        if len(self.notification_queue) > 3:
                            self.notification_queue.pop()

        trayicon.increase_unread((create_time, message))
        db.add(create_time, message)
        
    def on_bubble_animation_done(self, data):
        # bubble = None
        # if len(self.notify_queue):
        #     (message, height, create_time) =  self.notify_queue.pop()
        #     for notification in self.notification_queue:
        #         if notification.fade_in_moving or notification.move_up_moving:
        #             self.notify_queue.append((message, height, create_time))
        #         else:
        #             event_manager.emit("ready-to-move-up", height)                            
        #             bubble = Bubble(message, height, create_time)

        # if bubble:
        #     self.notification_queue.append(bubble)
        #     if len(self.notification_queue) > 3:
        #         self.notification_queue.pop()
        
        print self.notify_queue
        
        if len(self.notify_queue):
            (message, height, create_time) =  self.notify_queue.pop()

            event_manager.emit("ready-to-move-up", height)                            
            self.notification_queue.append(Bubble(message, height, create_time))
            if len(self.notification_queue) > 3:
                self.notification_queue.pop()

        
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
