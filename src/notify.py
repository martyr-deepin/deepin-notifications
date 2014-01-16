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

from PyQt5 import QtCore
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QSurfaceFormat, QColor
from PyQt5.QtCore import (QPropertyAnimation, QParallelAnimationGroup, 
                          QEasingCurve, QTimer)

SURFACE_FORMAT = QSurfaceFormat()
SURFACE_FORMAT.setAlphaBufferSize(8)
class Bubble(QQuickView):
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
        
        self._in_animation = self._getInAnimation()
        self._out_animation = self._getOutAnimation()
        self._in_animation.finished.connect(lambda: self._timer.start())
        self._out_animation.finished.connect(lambda: app.exit())
        self._timer = self._getTimer(self.timeout)
        self._timer.timeout.connect(lambda: self._out_animation.start())
        
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
        
    def showWithAnimation(self, animation=None):
        self.setX(SCREEN_WIDTH - 24 - self.width())
        self.setY(-self.height())
        self.show()
        (animation or self._in_animation).start()
        
SCREEN_WIDTH = 0
if __name__ == "__main__":
    app = QApplication(sys.argv)
    geo = app.desktop().screenGeometry()
    SCREEN_WIDTH = geo.width()
    
    bubble = Bubble(1024, "标题", "这里填写要显示的内容，不能太多 :)", 
                    (("default", None), ("reply", "回复"), ("reject", "拒绝")),
                    2000)
    bubble.showWithAnimation()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
