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

import gtk
import re

def get_screen_size():
    root_window = gtk.gdk.get_default_root_window()
    return root_window.get_size()

def get_hyperlink_support_str(raw_str):
    result = {"result" : "", "actions" : []}
    
    def replace_hyper_with_underline(match_obj):
        result["actions"].append({match_obj.group(1) : match_obj.group(2)})
        return "<u>" + match_obj.group(3) + "</u>"
    
    regex = re.compile(r'<a\s+([^\s]+)\s*=\s*([^\s/<>]+)\s*>([^<>\/].*?)</a>')
    
    result["result"] = regex.sub(replace_hyper_with_underline, raw_str)
    return result

def handle_message(message):
    hyperlink_support_str = get_hyperlink_support_str(message["body"])
    message["body"] = hyperlink_support_str["result"]
    message["hints"]["x-vendor-hyperlinks"] = hyperlink_support_str["actions"]
    return message
    
if __name__ == "__main__":
    raw_str = '''this is a test <a href="www.baidu.com">baidu</a>, another test <a href="www.google.com">google</a>'''
    print get_hyperlink_support_str(raw_str)
