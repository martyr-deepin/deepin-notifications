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

from events import event_manager

class Preference:
    '''
    class docs
    '''
	
    def __init__(self, config_path):
        '''
        init docs
        '''
        config_parser = ConfigParser()
        config_parser.add_section("section")
        config_parser.set("section", "option", 5)
        config_file = open(self.app_config_path, "w")
        config_parser.write(config_file)
        config_file.close()
            
        self.parser = ConfigParser().read(self.app_config_path)
            
    
    def get(self, section, option, default):
        '''
        docs
        '''
        if self.parser.has_option(section, option):
            return self.parser.get(section, option)
        return default
    
    def edit(self):
        
        return Editor(self)
    
class Editor:
    '''
    class docs
    '''
	
    def __init__(self, preference):
        '''
        init docs
        '''
        self.preference = preference
        self.parser = ConfigParser().read(self.preference.app_config_path)
    
    def set(self, section, option, value):
        '''
        docs
        '''
        if not self.parser.has_section(section):
            self.parser.add_section(section)
            
        self.parser.set(section, option, value)
    
    def commit(self):
        '''
        docs
        '''
        config_file = open(self.preference.app_config_path, "w")
        self.parser.write(config_file)
        config_file.close()
        event_manager.emit("preference-changed")
        
app_data_path = os.path.join(xdg.get_config_dir(), "data")
app_config_path = os.path.join(app_data_path, "notifications.ini")

config = None

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path)
if not os.path.exists(app_config_path):
    config = Preference(app_config_path, True)
else:
    config = Preference(app_config_path, False)

if __name__ == "__main__":
    Preference("preference-test")
