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
import subprocess
from collections import namedtuple
ClosedReason = namedtuple("ClosedReason", ("EXPIRED", "DISMISSED", "CLOSED", "UNDEFINED"))

from PyQt5 import QtCore
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QSurfaceFormat, QColor
from PyQt5.QtCore import (QObject, Q_CLASSINFO, pyqtSlot, pyqtProperty,
                          QPropertyAnimation, QParallelAnimationGroup, 
                          QEasingCurve, QTimer)
from PyQt5.QtDBus import (QDBusConnection, QDBusAbstractAdaptor,
                          QDBusConnectionInterface, QDBusMessage)

_BUBBLE_TIMEOUT_ = 5000
_CLOSED_REASON_ = ClosedReason(1, 2, 3, 4)

class BubbleService(QObject):
    def __init__(self, bubble):
        super(BubbleService, self).__init__()
        self.__dbusAdaptor = BubbleServiceAdaptor(self)
        self._sessionBus = QDBusConnection.sessionBus()
        
        self._bubble = bubble
        
    def updateContent(self, content):
        self._bubble._timer.start()
        self._bubble.updateContent(content)

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
        self._content = content
        
        self.setFormat(SURFACE_FORMAT)
        self.setFlags(QtCore.Qt.Popup)

        self.setColor(QColor(0, 0, 0, 0))
        self.setSource(QtCore.QUrl.fromLocalFile(
            os.path.join(os.path.dirname(__file__), 'ui/bubble.qml')
        ))
        
        qml_context = self.rootContext()
        qml_context.setContextProperty("_notify", self)
        
        self._in_animation = self._getInAnimation()
        self._out_animation = self._getOutAnimation()
        self._in_animation.finished.connect(lambda: self._timer.start())
        self._out_animation.finished.connect(lambda: self.exit())
        self._timer = self._getTimer(_BUBBLE_TIMEOUT_)
        self._timer.timeout.connect(lambda: self._out_animation.start())
        
        self._timer_remaining_time = _BUBBLE_TIMEOUT_
        
    @pyqtProperty(int)
    def id(self):
        return json.loads(self._content)["id"]
        
    @pyqtProperty(str)
    def content(self):
        return self._content
        
    @pyqtSlot()
    def pauseTimer(self):
        self._timer_remaining_time = self._timer.remainingTime()
        self._timer.stop()
        
    @pyqtSlot()
    def resumeTimer(self):
        self._timer.start(self._timer_remaining_time)
        
    @pyqtSlot()
    def openSenderProgram(self):
        self.resumeTimer()
        app_name = json.loads(self._content)["app_name"]
        subprocess.Popen(app_name)
        
    def _getInAnimation(self):
        animation = QPropertyAnimation(self, "y")
        animation.setEndValue(24)
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation
        
    def _getOutAnimation(self):
        animation = QParallelAnimationGroup()
        
        anim1 = QPropertyAnimation(self, "x")
        anim1.setEndValue(SCREEN_WIDTH)
        anim1.setDuration(500)
        anim1.setEasingCurve(QEasingCurve.OutCubic)
        animation.addAnimation(anim1)
        
        anim2 = QPropertyAnimation(self, "opacity")
        anim2.setEndValue(0.2)
        anim2.setDuration(500)
        anim2.setEasingCurve(QEasingCurve.OutCubic)
        animation.addAnimation(anim2)
        
        return animation
        
    def _getTimer(self, timeout):
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(timeout)
        return timer
        
    def updateContent(self, content):
        self._content = content
        self.rootObject().updateContent(self._content)
        
    def showWithAnimation(self, animation=None):
        self.updateContent(self._content)
        self.setX(SCREEN_WIDTH - 24 - self.width())
        self.setY(-self.height())
        self.show()
        (animation or self._in_animation).start()
        
    def exit(self):
        sendNotificationClosed(self.id, 2)
        app.exit()
        
def sendNotificationClosed(id, reason):
    msg = QDBusMessage.createSignal('/com/deepin/Bubble', 
                                    'com.deepin.Bubble', 
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
    bubble.showWithAnimation()
    
    bubbleService = BubbleService(bubble)
    bus = QDBusConnection.sessionBus()
    bus.interface().registerService('com.deepin.Bubble',
                                    QDBusConnectionInterface.ReplaceExistingService,
                                    QDBusConnectionInterface.AllowReplacement)
    bus.registerObject('/com/deepin/Bubble', bubbleService)
    bus.interface().serviceUnregistered.connect(serviceReplacedByOtherSlot)
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
