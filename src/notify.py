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
import json
import functools
import subprocess
from collections import namedtuple, deque
ClosedReason = namedtuple("ClosedReason", ("EXPIRED", "DISMISSED", "CLOSED", "UNDEFINED"))

from PyQt5 import QtCore
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QSurfaceFormat, QColor
from PyQt5.QtCore import (QObject, Q_CLASSINFO, pyqtSlot, pyqtProperty)
from PyQt5.QtDBus import (QDBusConnection, QDBusAbstractAdaptor,
                          QDBusConnectionInterface, QDBusMessage)

from image_provider import imageProvider

_BUBBLE_TIMEOUT_ = 5000
_CLOSED_REASON_ = ClosedReason(1, 2, 3, 4)

def checkQueueToQuit(func):
    def wapper(self):
        func(self)

        if len(self._contents) > 0: 
            self.showBubble()
        else:
            app.exit() 
    functools.update_wrapper(wapper, func)
    return wapper

class BubbleService(QObject):
    def __init__(self, bubble):
        super(BubbleService, self).__init__()
        self.__dbusAdaptor = BubbleServiceAdaptor(self)
        self._sessionBus = QDBusConnection.sessionBus()
        
        self._bubble = bubble
        
    def updateContent(self, content):
        self._bubble.appendContent(content)

class BubbleServiceAdaptor(QDBusAbstractAdaptor):

    Q_CLASSINFO("D-Bus Interface", "com.deepin.Bubble")
    Q_CLASSINFO("D-Bus Introspection",
                '  <interface name="com.deepin.Bubble">\n'
                '    <method name="UpdateContent">\n'
                '      <arg direction="in" type="s" name="content"/>\n'
                '    </method>\n'
                '  </interface>\n')

    def __init__(self, parent):
        super(BubbleServiceAdaptor, self).__init__(parent)

    @pyqtSlot(str)
    def UpdateContent(self, content):
        return self.parent().updateContent(content)

SURFACE_FORMAT = QSurfaceFormat()
SURFACE_FORMAT.setAlphaBufferSize(8)
class Bubble(QQuickView):
    def __init__(self, content):
        QQuickView.__init__(self)
        self._contents = deque()
        self._contents.appendleft(content)
        
        self.setFormat(SURFACE_FORMAT)
        self.setFlags(QtCore.Qt.FramelessWindowHint 
                      |QtCore.Qt.Tool
                      |QtCore.Qt.BypassWindowManagerHint)

        self.setColor(QColor(0, 0, 0, 0))

        qml_context = self.rootContext()
        qml_context.setContextProperty("_notify", self)
        qml_context.engine().addImageProvider("imageProvider", imageProvider)

        self.setSource(QtCore.QUrl.fromLocalFile(
            os.path.join(os.path.dirname(__file__), 'ui/bubble.qml')
        ))
        
    @pyqtProperty(int)
    def id(self):
        return json.loads(self._content)["id"]
        
    @pyqtProperty(str)
    def content(self):
        return self._content
        
    @pyqtSlot()
    def openSenderProgram(self):
        self.resumeTimer()
        app_name = json.loads(self._content)["app_name"]
        subprocess.Popen(app_name)
        
    @pyqtSlot(int, str)
    def sendActionInvokedSignal(self, notify_id, action_id):
        msg = QDBusMessage.createSignal('/org/freedesktop/Notifications', 
                                        'org.freedesktop.Notifications', 
                                        'ActionInvoked')
        msg << notify_id << action_id
        QDBusConnection.sessionBus().send(msg)
        
    def appendContent(self, content):
        self._contents.appendleft(content)
        if not self.rootObject().isAnimating(): 
            self.expire()
            self.showBubble()
        
    def showBubble(self):
        self._content = self._contents.pop()
        self.rootObject().updateContent(self._content)
        self.setX(SCREEN_WIDTH - self.width())
        self.setY(24)
        self.show()
        
    @pyqtSlot()
    @checkQueueToQuit
    def expire(self):
        sendNotificationClosed(self.id, _CLOSED_REASON_.EXPIRED)
        
    @pyqtSlot()
    @checkQueueToQuit
    def dismiss(self):
        sendNotificationClosed(self.id, _CLOSED_REASON_.DISMISSED)
        
def sendNotificationClosed(id, reason):
    msg = QDBusMessage.createSignal('/org/freedesktop/Notifications', 
                                    'org.freedesktop.Notifications', 
                                    'NotificationClosed')
    msg << id << reason
    QDBusConnection.sessionBus().send(msg)
        
@pyqtSlot(str)
def serviceReplacedByOtherSlot(name):
    os._exit(0)
    
    
SCREEN_WIDTH = 0
if __name__ == "__main__":
    app = QApplication(sys.argv)
    geo = app.desktop().screenGeometry()
    SCREEN_WIDTH = geo.width()
    
    bubble = Bubble(sys.argv[1])
    bubble.showBubble()
    
    bubbleService = BubbleService(bubble)
    bus = QDBusConnection.sessionBus()
    bus.interface().registerService('com.deepin.Bubble',
                                    QDBusConnectionInterface.ReplaceExistingService,
                                    QDBusConnectionInterface.AllowReplacement)
    bus.registerObject('/com/deepin/Bubble', bubbleService)
    bus.interface().serviceUnregistered.connect(serviceReplacedByOtherSlot)
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
