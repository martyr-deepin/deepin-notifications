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

from PyQt5.QtGui import QPixmap
from PyQt5.QtQuick import QQuickImageProvider

class RawImageProvider(QQuickImageProvider):
    def __init__(self, raw_data):
        super(RawImageProvider, self).__init__(QQuickImageProvider.Pixmap)
        self._raw_data = raw_data
        
    def requestPixmap(self, id, size, requestedSize):
        self._pixmap = QPixmap()
        self._pixmap.loadFromData(self._raw_data)
