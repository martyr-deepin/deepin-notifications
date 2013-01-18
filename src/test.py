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

import sys

import dbus

NID = 1568793152 # just a random number
DURATION = 30 # seconds, set to 0 to show forever
ICON = "dialog-warning" # adjust as you like

def alert(repo, error):

    bus = dbus.SessionBus()
    proxy = bus.get_object("org.freedesktop.Notifications",
                           "/org/freedesktop/Notifications")
    notid = dbus.Interface(proxy, "org.freedesktop.Notifications")

    summary = "AutoSync"
    text = ("Problems in repository <b>%s</b>: <i>%s</i>." %
            (repo, error))

    notid.Notify("AutoSync", NID, ICON, summary, text, [], {}, DURATION)

if __name__ == '__main__':

    alert(sys.argv[1], sys.argv[2])