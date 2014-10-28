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
import re
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtQuick import QQuickImageProvider

IMAGE_WIDTH = 48
IMAGE_HEIGHT = 48
HOME_DIR = os.path.expanduser("~")

class MyImageProvider(QQuickImageProvider):
    def __init__(self):
        super(MyImageProvider, self).__init__(QQuickImageProvider.Pixmap)

    def requestPixmap(self, id, size):
        themeName, iconName = re.match("\[(.*?)\](.*)", id).groups()
        defaultIcon = QPixmap(IMAGE_WIDTH, IMAGE_HEIGHT)
        defaultIcon.load(os.path.join(os.path.dirname(__file__), 'ui/default.png'))

        if (os.path.exists(iconName)):
            self._pixmap = QPixmap(IMAGE_WIDTH, IMAGE_HEIGHT)
            self._pixmap.load(iconName)
        else:
            QIcon.setThemeSearchPaths([os.path.join(HOME_DIR, ".icons"), 
                os.path.join(HOME_DIR, ".local/share/icons"),
                "/usr/local/share/icons", 
                "/usr/share/icons", 
                ":/icons"])
            QIcon.setThemeName(themeName)
            icon = QIcon.fromTheme(iconName)
            self._pixmap = defaultIcon if icon.isNull() else icon.pixmap(IMAGE_WIDTH, IMAGE_HEIGHT)

        return self._pixmap, QSize(IMAGE_WIDTH, IMAGE_HEIGHT)

imageProvider = MyImageProvider()