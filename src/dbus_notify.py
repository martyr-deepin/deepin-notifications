#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
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

import dbus
from dbus_utils import DBusProperty, DBusIntrospectable, type_convert

from events import event_manager
from common import Storage


REASON_EXPIRED = 1 # The notification expired.
REASON_DISMISSED = 2 # The notification was dismissed by the user.
REASON_CLOSED = 3 # The notification was closed by a call to CloseNotification.
REASON_UNDEFINED = 4  # Undefined/reserved reasons.

SERVER_CAPABILITIES = [
"action-icons", # Supports using icons instead of text for displaying actions. 
"actions", # The server will provide the specified actions to the user. 
"body", # Supports body text.
"body-hyperlinks", # The server supports hyperlinks in the notifications.
"body-images", # The server supports images in the notifications.
"body-markup", # Supports markup in the body text.
"icon-multi", # The server will render an animation of all the frames in a given image array.
"icon-static", # Supports display of exactly 1 frame of any given image array.
"persistence", # The server supports persistence of notifications.
"sound", # The server supports sounds on notifications .
]

DEFAULT_STANDARD_HINST = Storage({
    "action-icons" : False, # The icon name should be compliant with the Freedesktop.org Icon Naming Specification.
    "category" : "",  # The type of notification this is.
    "desktop-entry" : "",  # This specifies the name of the desktop filename representing the calling program.
    "image-data"  : "", # This is a raw data image format.
    "image-path" : "", # Alternative way to define the notification image.
    "resident" : False, # This hint is likely only useful when the server has the "persistence" capability.
    "sound-file" : "", # The path to a sound file to play when the notification pops up.
    "sound-name" : "", # A themeable named sound from the freedesktop.org sound naming specification.
    "suppress-sound" : False, # Causes the server to suppress playing any sounds, if it has that ability.
    "transient" : False, 
    "x" : None,
    "y" : None,
    "urgency" : 1 # 0 Low, 1 Normal, 2 Critical
    })


class Notifications(DBusProperty, DBusIntrospectable, dbus.service.Object):
    
    BUS_NAME = "org.freedesktop.Notifications"
    PATH = "/org/freedesktop/Notifications"
    NOTIFY_IFACE = "org.freedesktop.Notifications"
    
    NOTIFY_ISPEC = """
    <method name="CloseNotification">
      <arg direction="in"  name="id" type="i"/>
    </method>
    <method name="GetCapabilities">
      <arg direction="out"  name="caps" type="as"/>
    </method>
    <method name="GetServerInformation">
      <arg direction="out"  name="name"   type="s"/>
      <arg direction="out"  name="vendor" type="s"/>
      <arg direction="out"  name="version" type="s"/>
      <arg direction="out"  name="spec_version" type="s"/>
    </method>
    <method name="Notify">
      <arg direction="in"  name="app_name"  type="s"     />
      <arg direction="in"  name="id"        type="u"     />
      <arg direction="in"  name="icon"      type="s"     />
      <arg direction="in"  name="summary"   type="s"     />
      <arg direction="in"  name="body"      type="s"     />
      <arg direction="in"  name="actions"   type="as"    />
      <arg direction="in"  name="hints"     type="a{sv}" />
      <arg direction="in"  name="timeout"   type="i"     />
      <arg direction="out" name="id" type="u"     />
    </method>
    <signal name="NotificationClosed">
      <arg name="id" type="u" />
      <arg name="reason" type="u" />
    </signal>    
    <signal name="ActionInvoked">
      <arg name="id" type="u" />
      <arg name="action_key" type="s" />
    </signal>    
    """ 
    def __init__(self):
        DBusIntrospectable.__init__(self)
        DBusProperty.__init__(self)
        
        self.set_introspection(self.NOTIFY_IFACE, self.NOTIFY_ISPEC)
        
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.BUS_NAME, bus)
        dbus.service.Object.__init__(self, bus, self.PATH, name)
        
        self.id_cursor = long(0)
        
    @dbus.service.method(NOTIFY_IFACE, in_signature="u")    
    def CloseNotification(self, replaces_id):
        print replaces_id
        
    @dbus.service.method(NOTIFY_IFACE, out_signature="as")    
    def GetCapabilities(self):
        return SERVER_CAPABILITIES
    
    @dbus.service.method(NOTIFY_IFACE, out_signature="ssss")    
    def GetServerInformation(self):
        return "Notifications", "LinuxDeepin", "0.1", "1.2"
    
    @dbus.service.method(NOTIFY_IFACE, in_signature="susssasa{sv}i", out_signature="u")    
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, timeout):
        
        notify_storage = Storage({"app_name" : type_convert.dbus2py(app_name), 
                                  "replaces_id" : type_convert.dbus2py(replaces_id),
                                  "app_icon" : type_convert.dbus2py(app_icon),
                                  "summary" : type_convert.dbus2py(summary), 
                                  "body" : type_convert.dbus2py(body),
                                  "actions" : type_convert.dbus2py(actions),
                                  "hints" : type_convert.dbus2py(hints), 
                                  "expire_timeout" : type_convert.dbus2py(timeout)})
        

        event_manager.emit("notify", notify_storage)
        
        if replaces_id:
            return dbus.UInt32(replaces_id)
        else:
            self.id_cursor += 1
            return dbus.UInt32(self.id_cursor)
