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
from ui.skin import app_theme


class DeepinNotification(object):
    def __init__(self):
        
        # run_preload
        self.mainloop_init()
        
        import dbus_notify
        self.dbus = dbus_notify.Notifications()
        
        from ui.popup import PopupWindow
        app_instance = PopupWindow()

        event_manager.connect("message-coming", self.on_message_coming)
                
        import gtk
        gtk.main()
        
                
    #this method handle message coming for showing status icon
    def on_message_coming(self, data):
        trayicon.set_pixbuf_from_file("msg_white2.png")

            
    def run_preload(self):    
        pass
    
    
    def __init(self):
        pass
        
        
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
   
