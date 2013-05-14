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

from types import FunctionType

import gobject

import dbus
import dbus.proxies
import dbus.service
from dbus.lowlevel import SignalMessage

import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from . import hacks, properties
from .tools import bus_name_to_path, path_to_bus_name

class IpcProxyInterface(dbus.Interface):
    def get_extension(self, name, interface=None):
        return get_object(self.bus_name,
                '/'.join((self.object_path, name)),
                interface)

SESSION_BUS = dbus.SessionBus()
SYSTEM_BUS = dbus.SystemBus()

PATH_SEP = '/'

_INTERFACE_SENTINEL = 'THIS.IS.AN.INTERFACE.NAME.USED.AS.A.SENTINEL.AND.I.LIKE.TURTLES'

def get_object(modname, path=None, interface=None, bus=SESSION_BUS):
    if path is None:
        path = bus_name_to_path(modname)
    if interface is None:
        interface = path_to_bus_name(path)
    return IpcProxyInterface(
            bus.get_object(modname, path),
            interface
            )

#class IpcError(Exception):
 #   pass

class ObjectMeta(dbus.service.InterfaceType, gobject.GObjectMeta):

    def __new__(mcs, name, bases, dct):

        dct['_dbus_interface'] = _INTERFACE_SENTINEL
        cls = dbus.service.InterfaceType.__new__(mcs, name, bases, dct)

        # begin to add all ipc methods already defined.
        methods = cls._ipc_methods = {}
        # TODO: we don't need that, cause noone should derive
        # from a Module subclass, do we?
        # first, get the ipc methods of the base classes

        # now, add all new methods.
        for name, member in dct.iteritems():
            if (isinstance(member, FunctionType)
                    and getattr(member, '_ipc_expose', False)):
                cls._expose_method(member,
                        member._ipc_in_signature,
                        member._ipc_out_signature,
                        member._ipc_interface
                        )

        # add all signals
        if '__ipc_signals__' in dct:
            for name, signature in dct['__ipc_signals__'].iteritems():
                if not isinstance(signature, basestring):
                    signature, interface = signature
                else:
                    interface = None
                cls._expose_signal(name, signature, interface)

        return cls

class Object(dbus.service.Object, gobject.GObject):

    __gtype_name__ = 'Object'
    __metaclass__ = ObjectMeta

    @classmethod
    def _expose_method(cls, func, in_signature, out_signature, interface=None):
        """
        add a method to the dbus class. That can also be
        done after the class initialization.
        """

        if interface is None:
            interface = cls._dbus_interface
        hacks.add_method(
                cls,
                func,
                in_signature=in_signature,
                out_signature=out_signature,
                dbus_interface=interface,
                )

    @classmethod
    def _expose_signal(cls, name, signature, interface=None):
        if interface is None:
            interface = cls._dbus_interface
        hacks.add_signal(
                cls,
                name,
                signature,
                interface=interface,
                )

    @classmethod
    def _set_interface(cls, new_interface):
        clsname = cls.__module__ + '.' + cls.__name__
        if clsname in cls._dbus_class_table:
            entry = cls._dbus_class_table[clsname]
            if cls._dbus_interface in entry:
                entry[new_interface] = entry.pop(cls._dbus_interface)
                for func in entry[new_interface].itervalues():
                    func._dbus_interface = new_interface

        cls._dbus_interface = new_interface

    def emit_signal(self, name, *args):
        """
            emit the dbus signal called *name* with arguments.
        """

        if name not in self.__ipc_signals__:
            raise IpcError("Unknown signal: '%s'" % name)

        # Okay. Let's emit it.
        for location in self.locations:
            signature = self.__ipc_signals__[name]
            if not isinstance(signature, basestring):
                signature, interface = signature
            else:
                interface = self._interface
            message = SignalMessage(
                    self._path,
                    interface,
                    name)
            message.append(signature=signature, *args)
            location[0].send_message(message)


    def __init__(self, bus_name, path, interface=None, bus=SESSION_BUS):

        self._dbus_bus_name = dbus.service.BusName(bus_name, bus)

        dbus.service.Object.__init__(self, self._dbus_bus_name, path)
        gobject.GObject.__init__(self)

        self._bus = bus
        self._bus_name = bus_name
        self._path = path
        self._interface = interface or path_to_bus_name(path)

        # set the new interface
        self.__class__._set_interface(self._interface)

"""
class Module(Object):
    def __init__(self, bus_name):
        Object.__init__(self,
                BUS,
                bus_name,
                bus_name_to_path(bus_name)
                )
        self._bus_name = bus_name
        self._dbus_bus_name = dbus.service.BusName(bus_name, BUS)

class Extension(Object):
    def __init__(self, parent, name):
        path = PATH_SEP.join((parent._path, name))
        interface = path_to_bus_name(path)
        Object.__init__(self,
                BUS,
                interface,
                path)
        self._parent = parent
"""

def method(doodle='', out_signature='', interface=None):

    # two choices:
    # 1) called as @ipc.method
    if isinstance(doodle, FunctionType):
        doodle._ipc_name = doodle.__name__
        doodle._ipc_in_signature = ''
        doodle._ipc_out_signature = ''
        doodle._ipc_expose = True
        doodle._ipc_interface = interface
        return doodle

    # 2) called as @ipc.method()
    else:
        in_signature = doodle
        def decorator(f):
            f._ipc_name = f.__name__
            f._ipc_in_signature = in_signature
            f._ipc_out_signature = out_signature
            f._ipc_expose = True
            f._ipc_interface = interface
            return f

        return decorator

