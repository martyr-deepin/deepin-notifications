#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yaohua
# 
# Author:     Wang Yaohua <mr.asianwang@gmail.com>
# Maintainer: Wang Yaohua <mr.asianwang@gmail.com>
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
import cPickle

import xdg

class Blacklist(object):
    '''
    class docs
    '''
	
    def __init__(self, path):
        '''
        init docs
        '''
        self.path = path
        if not os.path.exists(self.path):
            open(self.path, "w").close()
            
        self.bl_file = open(self.path, "r")
        file_content = self.bl_file.read()
        if len(file_content) != 0:
            self.bl = cPickle.loads(file_content)
        else:
            self.bl = []

    def add(self, black):
        self.bl.append(black)
        self.bl_file = open(self.path, "w")
        self.bl_file.write(cPickle.dumps(self.bl))

    def remove(self, black):
        if black in self.bl:
            self.bl.remove(black)
            self.bl_file = open(self.path, "w")
            self.bl_file.write(cPickle.dumps(self.bl))
            
            
app_data_path = os.path.join(xdg.get_config_dir(), "data")
app_bl_path = os.path.join(app_data_path, ".blacklist")

blacklist = Blacklist(app_bl_path)
