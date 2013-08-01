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
import sys
import dbus
from events import event_manager

class DeepinNotification(object):
    def __init__(self):
        
        import dbus_notify
        self.dbus = dbus_notify.Notifications()
        event_manager.connect("action-invoked", lambda (id, key): self.dbus.ActionInvoked(id, key))
        
        from ui.bubble_manager import BubbleManager
        self.bubble_manager = BubbleManager()
        
        import gtk
        gtk.main()
                
        
def mainloop_init():    
    import gobject
    gobject.threads_init()
    
    # dbus_init.
    import dbus.mainloop.glib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    dbus.mainloop.glib.threads_init()
    dbus.mainloop.glib.gthreads_init()
    
    # gtk_init.
    import gtk
    gtk.gdk.threads_init()
    
def is_service_exists(app_dbus_name, app_object_name):
    bus = dbus.SessionBus()
    if bus.request_name(app_dbus_name) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        return True
    else:
        return False


if __name__ == "__main__":
    mainloop_init()
    
    # Build DBus name.
    app_dbus_name = "com.deepin.notification"
    app_object_name = "/com/deepin/notification"
    
    # Check unique.
    if is_service_exists(app_dbus_name, app_object_name):
        sys.exit()
    
    DeepinNotification()
