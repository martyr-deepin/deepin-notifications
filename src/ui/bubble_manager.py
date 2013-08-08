#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou ShaoHui
#
# Author:     Hou ShaoHui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
#             Wang Yaohua <mr.asianwang@gmail.com>
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

import gobject
from dtk.ui.timeline import Timeline, CURVE_SINE

from notification_db import db
from unread_db import unread_db
from blacklist import blacklist
from preference import preference
from events import event_manager
from ui.tray import trayicon
from ui.bubble import Bubble
from ui.utils import handle_notification

ANIMATION_TIME = 500

class BubbleManager(object):

    def __init__(self):
        # Init values
        self.bubble_queue = deque()
        self.incoming_queue = deque()

        self.is_in_animation = False

        # Connect events
        event_manager.connect("notify", self.on_notify)
        event_manager.connect("bubble-destroy", self.on_bubble_destroy)
        event_manager.connect("manual-destroy", self.on_manual_destroy)


    def on_notify(self, notification):
        # replace hyper<a> with underline <u> _AND_ place hyper actions in hints["x-deepin-hyperlinks"]
        message = handle_notification(notification)

        height = 87 if len(message["actions"]) == 0 else 110
        incoming_time = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")

        self.incoming_queue.append((message, height, incoming_time))

        trayicon.increase_unread((incoming_time, message))
        db.add(incoming_time, message)
        if trayicon.detail_window.get_visible():
            trayicon.detail_window._init_data()
        else:
            trayicon.detail_window.refresh_view()

        self.show_bubble()

    # if bubble died because manual close or expire, we need to remove the bubble from our bubble queue manually.
    def on_bubble_destroy(self, bubble):
        self.bubble_queue.remove(bubble)

    def on_manual_destroy(self, bubble):
        self.bubble_queue.remove(bubble)

    def show_bubble(self):
        if not len(self.incoming_queue) == 0:
            message, height, incoming_time = self.incoming_queue.popleft()
            if not preference.disable_bubble:
                if message.app_name not in blacklist.bl:
                    if not self.is_in_animation:
                        self.is_in_animation = True
                        self.bubble_queue.appendleft(Bubble(message, height, incoming_time))
                        self.start_move_up_animation(height)
                    else:
                        # remember to put it back :)
                        self.incoming_queue.appendleft((message, height, incoming_time))
        else:
            db.commit()
            unread_db.commit()

    # bubble manager controls move-up-animation in case that bubble move-up asynclly.
    def start_move_up_animation(self, height):
        timeline = Timeline(ANIMATION_TIME, CURVE_SINE)
        timeline.connect("update", self.update_move_up_animation, height)
        timeline.connect("completed", self.on_move_up_completed)
        timeline.run()

    def update_move_up_animation(self, source, status, move_up_height):
        index = 0
        bubble_queue_size = len(self.bubble_queue)

        while index < bubble_queue_size:
            current_bubble = self.bubble_queue[index]
            current_bubble.move_up_by(status * move_up_height, not bool(status - 1))

            if index == 0:
                if status > 0.5:
                    current_bubble.set_opacity(status)
                if status == 1:
                    current_bubble.level += 1
            elif index == 2:
                if status == 1:
                    self.bubble_queue.remove(current_bubble)
                    current_bubble.destroy()
                    gobject.source_remove(current_bubble.timeout_id)
                else:
                    current_bubble.set_opacity(1 - status)
            index += 1


    def on_move_up_completed(self, source):
        self.is_in_animation = False
        self.show_bubble()
