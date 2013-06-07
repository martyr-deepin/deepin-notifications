#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou ShaoHui
# 
# Author:     Hou ShaoHui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
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


from collections import deque
from datetime import datetime

from notification_db import db
from blacklist import blacklist
from preference import preference
from events import event_manager

from ui.tray import trayicon
from ui.bubble import Bubble
from ui.utils import handle_notification


class BubbleManager(object):
    
    def __init__(self):
        
        # Init values
        self.bubble_queue = deque()
        self.last_bubble = None
        
        # Connect events
        event_manager.connect("notify", self.on_notify)
        event_manager.connect("bubble-move-up-completed", self.on_bubble_move_up_completed)
        
    @property    
    def is_in_animation(self):    
        if self.last_bubble:
            if self.last_bubble.move_up_moving or self.last_bubble.fade_in_moving:
                return True
        return False    
        
    def on_notify(self, notification):    
        
        # replace hyper<a> with underline <u> AND place hyper actions in hints["x-deepin-hyperlinks"]
        message = handle_notification(notification)
        
        height = 87 if len(message["actions"]) == 0 else 110
        create_time = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        
        if not preference.disable_bubble:
            if message.app_name not in blacklist.bl:
                self.bubble_queue.append((message, height, create_time))
                if not self.is_in_animation:
                    event_manager.emit("ready-to-move-up", height)                    
                    message, height, create_time = self.bubble_queue.pop()
                    self.last_bubble = Bubble(message, height, create_time)

        trayicon.increase_unread((create_time, message))
        db.add(create_time, message)
                    
                    
    def on_bubble_move_up_completed(self, data):                
        if len(self.bubble_queue) > 0:
            print "move_up_completed"
            message, height, create_time = self.bubble_queue.pop()
            self.last_bubble = Bubble(message, height, create_time)
            event_manager.emit("ready-to-move-up", height)
