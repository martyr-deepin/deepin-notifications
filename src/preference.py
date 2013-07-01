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
from ConfigParser import ConfigParser

import xdg

class Preference(object):
    '''
    class docs
    '''
	
    def __init__(self, create_file):
        '''
        init docs
        '''
        if create_file:
            config_parser = ConfigParser()
            config_parser.add_section("general")
            config_parser.set("general", "disable-bubble", "False")
            config_file = open(app_config_path, "w")
            config_parser.write(config_file)
            config_file.close()
            
        config_file = open(app_config_path)
        self.parser = ConfigParser()
        self.parser.readfp(config_file)
        config_file.close()
            
        
    def get(self, section, option, default):
        '''
        docs
        '''
        if self.parser.has_option(section, option):
            return self.parser.get(section, option)
        return default
    
    def set(self, section, option, value):
        '''
        docs
        '''
        if not self.parser.has_section(section):
            self.parser.add_section(section)
            
        self.parser.set(section, option, value)
        self.commit()
        
        
    def commit(self):
        config_file = open(app_config_path, "w")
        self.parser.write(config_file)
        config_file.close()
        
        
    disable_bubble = property(lambda obj : obj.get("general", "disable-bubble", "False") == "True", # getter
                              lambda obj, value : obj.set("general", "disable-bubble", str(value)) # setter
                              )
    
        
app_data_path = os.path.join(xdg.get_config_dir(), "data")
app_config_path = os.path.join(app_data_path, "notifications.ini")

config = None

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path)
if not os.path.exists(app_config_path):
    preference = Preference(True)
else:
    preference = Preference(False)
