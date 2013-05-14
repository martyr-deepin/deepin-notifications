#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou ShaoHui
# 
# Author:     Hou ShaoHui <houshao55@gmail.com>
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

import gobject
from collections import namedtuple
from dbus.exceptions import DBusException

import ipc

NAME = 'Notifications'
VENDOR = 'LinuxDeepin'
VERSION = '0.1'

DEFAULT_EXPIRE_TIMEOUT = 10000

MAX_ID = 2**32 - 1

SERVICE_NAME = 'org.freedesktop.Notifications'
SERVICE_OBJECT = '/org/freedesktop/Notifications'

def generate_ids():
    """
        A generator for unique IDs.
    """
    while True:
        i = 1
        while i <= MAX_ID:
            yield i
            i += 1

class Capability(object):
    actions = 'actions'
    body = 'body'
    body_hyperlinks = 'body-hyperlinks'
    body_images = 'body-images'
    body_markup = 'body-markup'
    icon_multi = 'icon-multi'
    icon_static = 'icon-static'
    sound = 'sound'

class Urgency(object):
    low = 0
    normal = 1
    critical = 2

class Expires(object):
    default = -1
    never = 0

class Reason(object):
    expired = 1
    dismissed = 2
    closed = 3
    undefined = 4

Action = namedtuple('Action', 'key displayed')

class ImageData(object):
    def __init__(self, width, height, rowstride, has_alpha, bps, channels, data):
        self.width = int(width)
        self.height = int(height)
        self.rowstride = int(rowstride)
        self.has_alpha = bool(has_alpha)
        self.bps = int(bps)
        self.channels = int(channels)
        self.data = map(int, data)

    def to_gtk_pixbuf(self):
        import gtk
        return gtk.gdk.pixbuf_new_from_data(
                ''.join(map(chr, self.data)),
                gtk.gdk.COLORSPACE_RGB,
                self.has_alpha,
                self.bps,
                self.width,
                self.height,
                self.rowstride)

class Notification(object):
    def __init__(self, id, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        self.id = id
        self.app_name = app_name
        self.replaces_id = replaces_id
        self.app_icon = app_icon
        self.summary = summary
        self.body = body
        self.action_array = actions
        self.hints = hints
        self.expire_timeout = expire_timeout

    @property
    def urgency(self):
        return int(self.hints.get('urgency', Urgency.normal))

    @property
    def category(self):
        return str(self.hints.get('category', ''))

    @property
    def desktop_entry(self):
        return str(self.hints.get('desktop-entry', ''))

    @property
    def image_data(self):
        # icon_data == image-data? WTF.
        if 'image-data' in self.hints:
            return ImageData(*self.hints['image-data'])
        elif 'icon_data' in self.hints:
            return ImageData(*self.hints['icon_data'])
        else:
            return None

    @property
    def sound_file(self):
        return str(self.hints.get('sound-file', ''))

    @property
    def suppress_sound(self):
        return bool(self.hints.get('suppress-sound', False))

    @property
    def x(self):
        return int(self.hints.get('x', -1))

    @property
    def y(self):
        return int(self.hints.get('y', -1))

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def actions(self):
        array = self.action_array
        return [Action(*arg) for arg in zip(array[::2], array[1::2])]

    def __repr__(self):
        return '<Notification object #%d at 0x%x (%r)>' % (self.id, id(self), str(self.summary))

    def __hash__(self):
        return hash(self.id)

class Server(ipc.Object):
    __gsignals__ = {
        'get-capabilities': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_PYOBJECT, ()), # required to return an array of strings
        'show-notification': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'hide-notification': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    __ipc_signals__ = {
        'NotificationClosed': 'uu',
        'ActionInvoked': 'us',
    }

    def __init__(self):
        ipc.Object.__init__(self,
            SERVICE_NAME,
            SERVICE_OBJECT
            )
        self.id_generator = generate_ids()
        self.notifications = {}

    def show(self, notification):
        self.notifications[notification.id] = notification
        self.emit('show-notification', notification)

    def hide(self, notification):
        del self.notifications[notification.id]
        self.emit('hide-notification', notification)

    def close(self, notification, reason):
        self.hide(notification)
        self.emit_signal('NotificationClosed', notification.id, reason)

    def invoke_action(self, notification, action_key):
        self.emit_signal('ActionInvoked', notification.id, action_key)

    @ipc.method('', 'as')
    def GetCapabilities(self):
        print ' --- get capabilities!'
        return self.emit('get-capabilities')

    @ipc.method('u', '')
    def CloseNotification(self, id):
        if id in self.notifications:
            self.close(self.notifications[id], Reason.closed)
        else:
            raise DBusException()

    @ipc.method('susssasa{sv}i', 'u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        notification = Notification(self.id_generator.next(),
                                    app_name,
                                    replaces_id,
                                    app_icon,
                                    summary,
                                    body,
                                    actions,
                                    hints,
                                    expire_timeout)
        # setup expire timeout
        if expire_timeout == Expires.default:
            expire_timeout = DEFAULT_EXPIRE_TIMEOUT
        if expire_timeout != Expires.never:
            def _expire():
                self.close(notification, Reason.expired)
                return False
            gobject.timeout_add(expire_timeout, _expire)
        # showtime
        self.show(notification)
        return notification.id

    @ipc.method('', 'sss')
    def GetServerInformation(self):
        return (NAME, VENDOR, VERSION)

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

    server = Server()

    import gobject
    mainloop = gobject.MainLoop()
    mainloop.run()

