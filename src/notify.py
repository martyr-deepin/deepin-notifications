#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2014 Deepin, Inc.
#               2011 ~ 2014 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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

import os
import sys
import signal
from collections import deque

from PyQt5 import QtCore
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QSurfaceFormat, QColor
from PyQt5.QtCore import (QObject, pyqtSlot, pyqtSignal,
                          QPropertyAnimation, QEasingCurve,
                          QTimer, Q_CLASSINFO, QVariant)
from PyQt5.QtDBus import QDBusAbstractAdaptor, QDBusConnection
from PyQt5.QtDBus import QDBusConnectionInterface, QDBusMessage, QDBusVariant

from logger import func_logger, logger

class Notifications(QObject):
    def __init__(self):
        super(Notifications, self).__init__()
        self.__adaptor = NotificationsAdapter(self)
        self._bus = QDBusConnection.sessionBus()
        
        self._bubble_manager = _BubbleManager()
        
    def closeNotification(self, id):
        print id
        
    def getCapabilities(self):
        return ("hello", "world")
        
    def getServerInformation(self):
        return ("DeepinNotifications", "LinuxDeepin", "2.0", "1.2")
        
    def notify(self, app_name, id, icon, summary, body, actions, hints, timeout):
        bubble = Bubble(1024, "标题", "这里填写要显示的内容，不能太多 :)", 
                        (("default", None), ("reply", "回复"), ("reject", "拒绝")),
                        2000)
        self._bubble_manager.append(bubble)
        self._bubble_manager.checkForPop()
        return 1

class NotificationsAdapter(QDBusAbstractAdaptor):
    """DBus service for Deepin Notifications."""

    # Q_CLASSINFO("D-Bus Interface", "org.freedesktop.Notifications")
    # Q_CLASSINFO("D-Bus Introspection",
    #             '<interface name="org.freedesktop.Notifications">\n'
    #             '    <method name="GetCapabilities">\n'
    #             '        <arg direction="out"  name="caps" type="as"/>\n'
    #             '    </method>\n'
    #             '    <method name="GetServerInformation">\n'
    #             '        <arg direction="out"  name="name"   type="s"/>\n'
    #             '        <arg direction="out"  name="vendor" type="s"/>\n'
    #             '        <arg direction="out"  name="version" type="s"/>\n'
    #             '        <arg direction="out"  name="spec_version" type="s"/>\n'
    #             '    </method>\n'
    #             '    <method name="Notify">\n'
    #             '        <arg direction="in"  name="app_name"  type="s"/>\n'
    #             '        <arg direction="in"  name="id"        type="u"/>\n'
    #             '        <arg direction="in"  name="icon"      type="s"/>\n'
    #             '        <arg direction="in"  name="summary"   type="s"/>\n'
    #             '        <arg direction="in"  name="body"      type="s"/>\n'
    #             '        <arg direction="in"  name="actions"   type="as"/>\n'
    #             '        <arg direction="in"  name="hints"     type="a{sv}"/>\n'
    #             '        <arg direction="in"  name="timeout"   type="i"/>\n'
    #             '        <arg direction="out" name="id" type="u"/>\n'
    #             '    </method>\n'
    #             '    <signal name="NotificationClosed">\n'
    #             '        <arg name="id" type="u"/>\n'
    #             '        <arg name="reason" type="u"/>\n'
    #             '    </signal>\n'
    #             '    <signal name="ActionInvoked">\n'
    #             '        <arg name="id" type="u"/>\n'
    #             '        <arg name="action_key" type="s" />\n'
    #             '    </signal>\n'
    #             '</interface>\n')
    
    Q_CLASSINFO("D-Bus Interface", "org.freedesktop.Notifications")
    Q_CLASSINFO("D-Bus Introspection",
                '  <interface name="org.freedesktop.Notifications">\n'
                '    <method name="CloseNotification">\n'
                '        <arg direction="in"  name="id" type="u"/>\n'
                '    </method>\n'
                '  </interface>\n')    

    def __init__(self, parent):
        super(NotificationsAdapter, self).__init__(parent)
        
    @pyqtSlot("QVariant")
    def CloseNotification(self, id):
        print "hello"
        # self.parent().closeNotification(id)
        
    @pyqtSlot(result="QVariant")
    def GetServerInformation(self):
        return self.parent().getServerInformation()
        
    @pyqtSlot(str, int, str, str, str, int, result=int)
    def Notify(self, app_name, id, icon, summary, body, timeout):
        return self.parent().notify(app_name, id, icon, summary, body, timeout)
        
class _BubbleManager(deque):
    actionInvoked = pyqtSignal(str)
    notificationClosed = pyqtSignal(int)
    
    def __init__(self):
        super(_BubbleManager, self).__init__()
        
    def checkForPop(self):
        if len(self < 2): 
            if not self[0].visible(): self[0].showWithAnimation() 
            return
        self.actionInvoked.emit(self.popleft().id)          # don't forget to send notificationClosed signal here
        self[0].showWithAnimation()
        self[0].actionInvoked.connect(lambda: self.actionInvoked.emit)
        self[0].notificationClosed.connect(lambda: self.notificationClosed.emit)
        self[0].readyForReplacement.connect(self.checkForPop)
        
SURFACE_FORMAT = QSurfaceFormat()
SURFACE_FORMAT.setAlphaBufferSize(8)
class Bubble(QQuickView):
    actionInvoked = pyqtSignal(str)
    notificationClosed = pyqtSignal(int)
    # To tell the manager this bubble is ready to be replaced.
    readyForReplacement = pyqtSignal()
    
    def __init__(self, id, summary, body, actions, timeout):
        QQuickView.__init__(self)
        self.id = id
        self.summary = summary or ""
        self.body = body or ""
        self.actions = actions or ()
        self.timeout = 2000
        
        self.setFormat(SURFACE_FORMAT)
        self.setFlags(QtCore.Qt.Popup)

        self.setColor(QColor(0, 0, 0, 0))
        self.setSource(QtCore.QUrl.fromLocalFile(
            os.path.join(os.path.dirname(__file__), 'ui/bubble.qml')
        ))
        
        self._animation = self._getDefaultAnimation()
        self._animation.finished.connect(lambda: self.readyForReplacement.emit())
        self._timer = self._getTimer(self.timeout)
        self._timer.timeout.connect(lambda: self.destroy())
        self._timer.timeout.connect(lambda: self.notificationClosed.emit(self.id))
        
    def _getDefaultAnimation(self):
        animation = QPropertyAnimation(self, "y")
        animation.setEndValue(24)
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation
        
    def _getTimer(self, timeout):
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.start(timeout)
        return timer
        
    def showWithAnimation(self, animation=None):
        self.setX(SCREEN_WIDTH - 24 - self.width())
        self.setY(-self.height())
        self.show()
        (animation or self._animation).start()
        
SCREEN_WIDTH = 0
if __name__ == "__main__":
    app = QApplication(sys.argv)
    geo = app.desktop().screenGeometry()
    SCREEN_WIDTH = geo.width()

    bus = QDBusConnection.sessionBus()
    notifications = Notifications()
    bus.registerService('com.deepin.notifications')
    bus.registerObject('/org/freedesktop/Notifications', notifications)
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
