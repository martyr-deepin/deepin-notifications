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
import cairo
import gobject

from collections import deque
from threading import Lock
from dtk.ui.draw import  draw_pixbuf, draw_text, TEXT_ALIGN_TOP
from dtk.ui.timeline import Timeline, CURVE_SINE
from dtk.ui.utils import (propagate_expose, is_in_rect, get_content_size)

import xdg
from events import event_manager
from ui.icons import icon_manager
from ui.utils import get_screen_size

MIN_ITEM_HEIGHT = 87
WINDOW_WIDTH = 310
WINDOW_HEIGHT = MIN_ITEM_HEIGHT * 3
WINDOW_OFFSET_WIDTH = 10
WINDOW_OFFSET_HEIGHT = 0
DOCK_HEIGHT = 35

CLOSE_OFFSET_WIDTH = 10
CLOSE_OFFSET_HEIGHT = 8

APP_ICON_X = 6
APP_ICON_WIDTH = 75

TEXT_PADDING_X = 10
TEXT_PADDING_Y = 8
TEXT_X = APP_ICON_X + APP_ICON_WIDTH +  TEXT_PADDING_X
TEXT_WIDTH = 218 - TEXT_PADDING_X * 2

SUMMARY_TEXT_Y = 10

BODY_OFFSET_HEIGHT = 20
BODY_TEXT_HEIGHT = 40

ICON_SIZE = (48, 48)

class MessageFixed(gtk.Fixed):
    
    def __init__(self):
        gtk.Fixed.__init__(self)
        self.item_height = MIN_ITEM_HEIGHT * 3
        
        self.in_animation = False
        self.animation_time = 500
        self.animation_timeout_id = None
        self.message_queue = deque()
        self.put_x = 0
        
    def add_message_box(self, widget):    
        widget.set_y(self.item_height)
        self.message_queue.append(widget)
        if not self.in_animation:
            message_box = self.message_queue.pop()
            self.put_message_box(message_box)
            
    def put_message_box(self, widget):        
        self.put(widget, self.put_x, self.item_height)        
        self.show_all()
        if self.parent.get_property("visible"):
            self.start_animation()
        else:    
            self.parent.show_all()
        
    def delay_start_animation(self):    
        self.start_animation()
        
    @property    
    def has_messages(self):
        if len(self.get_children()) > 0:        
            return True
        return False
            
    def start_animation(self):    
        if not self.in_animation:
            self.in_animation = True
            self.timeline = Timeline(self.animation_time, CURVE_SINE)
            self.timeline.connect("update", self.update_animation)
            self.timeline.connect("completed", self.completed_animation)
            self.timeline.run()
             
    def update_animation(self, source, status):        
        self.foreach(lambda w: w.move_to(status * MIN_ITEM_HEIGHT, status))
        
    def completed_animation(self, source):    
        self.in_animation = False
        self.foreach(lambda widget : widget.notify_completed())
        if len(self.message_queue) > 0:
            message_box = self.message_queue.pop()
            self.put_message_box(message_box)
        event_manager.emit("message-coming", None)    
            
gobject.type_register(MessageFixed)        
        
class MinMessageBox(gtk.EventBox):
    
    def __init__(self, message):
        gtk.EventBox.__init__(self)
        self.set_visible_window(False)
        self.message = message
        self.init_size()
        self.connect("expose-event", self.on_expose_event)
        self.connect("button-press-event", self.on_button_press_event)
        
        self.last_x = 0
        self.last_y = None
        
        self.default_icon = gtk.gdk.pixbuf_new_from_file(xdg.get_image_path("icon.png"))
        self.message_icon = self.get_icon_pixbuf()
        
        self.animation_time = 500
        self.in_animation = False
        self.in_move_animation = False 
        self.animation_timeout_id = None
        self.active_alpha = 1.0
        self.delay_timeout = 3000
        self.level = 0
        self.is_move_down = False
        event_manager.connect("level-one-destroy", self.try_to_movedown)
        
    def get_icon_pixbuf(self):    
        hints = self.message.hints
        pixbuf = None
        image_data = hints.get("image-data", None) or hints.get("image_data", None)
        if image_data:
            pixbuf = icon_manager.pixbuf_from_dbus(image_data, ICON_SIZE)
            
        if pixbuf: return pixbuf
        
        image_path = hints.get("image-path", None) or hints.get("image_path", None)
        if image_path:
            try:
                pixbuf = icon_manager.pixbuf_from_path(image_path, ICON_SIZE[0], ICON_SIZE[1])
            except:
                pixbuf = None
                
        if pixbuf: return pixbuf        
        
        app_icon = self.message.icon
        if app_icon:
            pixbuf = icon_manager.pixbuf_from_icon_name(app_icon, ICON_SIZE[0])
        if pixbuf:    
            return pixbuf
        return self.default_icon
        
    def set_y(self, y):    
        self.last_y = y
        
    def init_size(self):    
        self.bg_pixbuf = gtk.gdk.pixbuf_new_from_file(xdg.get_image_path("mini.png"))
        self.close_pixbuf = gtk.gdk.pixbuf_new_from_file(xdg.get_image_path("close.png"))
        
        width = self.bg_pixbuf.get_width()
        height= self.bg_pixbuf.get_height()        
        self.total_height = height
        
        self.close_rect = gtk.gdk.Rectangle(width - self.close_pixbuf.get_width() - CLOSE_OFFSET_WIDTH,
                                            CLOSE_OFFSET_HEIGHT,
                                            self.close_pixbuf.get_width(),
                                            self.close_pixbuf.get_height())

        self.set_size_request(width, height)
        
        
    def on_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        cr.save()
        self.draw_message(cr, rect, self.active_alpha)
        cr.restore()
        return True
    
    def draw_message(self, cr, rect, alpha):
        cr.push_group()
        draw_pixbuf(cr, self.bg_pixbuf, rect.x, rect.y)
        
        icon_x = rect.x + self.close_rect.x
        icon_y = rect.y + self.close_rect.y
        draw_pixbuf(cr, self.close_pixbuf, icon_x, icon_y)
        
        # Draw app icon.
        icon_x = APP_ICON_X + (APP_ICON_WIDTH  - self.message_icon.get_width()) / 2
        icon_y = rect.y + (rect.height - self.message_icon.get_height()) / 2
        draw_pixbuf(cr, self.message_icon, icon_x, icon_y)
        
        # Draw summary.
        
        
        width, _height =  get_content_size(self.message.summary)
        draw_text(cr, 
                  "<b>%s</b>" % self.message.summary, 
                  rect.x + TEXT_X, rect.y + SUMMARY_TEXT_Y, 
                  TEXT_WIDTH - self.close_pixbuf.get_width(), _height,
                  text_color="#FFFFFF", text_size=10)
        
        body_text_y = SUMMARY_TEXT_Y + _height + TEXT_PADDING_Y
        
        draw_text(cr, self.message.body, 
                  rect.x + TEXT_X, rect.y + body_text_y,
                  TEXT_WIDTH, BODY_TEXT_HEIGHT,
                  wrap_width=TEXT_WIDTH,
                  text_color="#FFFFFF", text_size=10, 
                  vertical_alignment=TEXT_ALIGN_TOP,
                  clip_line_count=2)
        
        # set source to paint with alpha.
        cr.pop_group_to_source()
        cr.paint_with_alpha(alpha)
    
    def on_button_press_event(self, widget, event):
        if is_in_rect((event.x, event.y), 
                      (self.close_rect.x, self.close_rect.y, 
                       self.close_rect.width, self.close_rect.height)):
            self.manual_destroy()
            
    def move_to(self, height, status):        
        if self.level == 0:
            self.active_alpha = status
        if self.level == 2:
            self.active_alpha = 1.0 - status
            
        if self.active_alpha < 0:    
            self.active_alpha = 0
        elif self.active_alpha > 1:    
            self.active_alpha = 1
            
        new_height = self.last_y - height
        try:
            self.parent.move(self, self.last_x, int(new_height))
        except:    
            pass
        
    def move_down(self, status):    
        if self.in_animation:
            try:
                self.move_animation.stop()
            except: pass    
            return
            
        height = status * MIN_ITEM_HEIGHT
        new_height = self.last_y + height
        try:
            self.parent.move(self, self.last_x, int(new_height))
        except:    
            pass
        
    def try_to_movedown(self, data):
        if self.level == 2:
            self.start_move_animation()
            
    def start_move_animation(self):
        if not self.in_move_animation:
            self.in_move_animation = True
            self.move_timeline = Timeline(self.animation_time, CURVE_SINE)
            self.move_timeline.connect("update", self.update_move_animation)
            self.move_timeline.connect("completed", self.completed_move_animation)
            self.move_timeline.run()
            
    def update_move_animation(self, source, status):
        self.move_down(status)
        
    def completed_move_animation(self, source):
        self.in_move_animation = False
        self.last_y += MIN_ITEM_HEIGHT
        
    def start_alpha_animation(self):
        if not self.in_animation:
            self.in_animation = True
            timeline = Timeline(self.animation_time, CURVE_SINE)
            timeline.connect("update", self.update_animation)
            timeline.connect("completed", lambda source : self.destroy_self())
            timeline.run()
        return False    
            
    def update_animation(self, source, status):        
        self.active_alpha = 1.0 - status
        self.queue_draw()
        
    def destroy_self(self):    
        if self.animation_timeout_id is not None:
            gobject.source_remove(self.animation_timeout_id)
        try:
            self.parent.remove(self)
            self.destroy()
        except: pass    
        
        if self.level == 1:
            event_manager.emit("level-one-destroy", None)
        event_manager.emit("message-destroy", None)    
    
    def delay_destroy(self):
        if self.animation_timeout_id is None:
            self.animation_timeout_id = gobject.timeout_add(self.delay_timeout, self.start_alpha_animation)
            
    def manual_destroy(self):        
        if self.animation_timeout_id is not None:
            gobject.source_remove(self.animation_timeout_id)
            self.animation_timeout_id = None
        self.start_alpha_animation()    
        
    def notify_completed(self):
        self.level += 1        
        self.last_y -= MIN_ITEM_HEIGHT
        if self.level == 1 and not self.in_animation:
            self.delay_destroy()
        elif self.level == 3 and not self.in_animation:
            self.destroy_self()


class PopupWindow(gtk.Window):
    
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_skip_taskbar_hint(True)
        self.set_decorated(False)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        # self.set_position(gtk.WIN_POS_CENTER)
        self.set_keep_above(True)
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rga_colormap())
        self.control = MessageFixed()
        self.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.connect("expose-event", self.on_expose_event)
        self.connect_after("show", lambda widget: self.control.delay_start_animation())
        event_manager.connect("notify", self.on_notify_event)
        event_manager.connect("message-coming", self.on_message_coming)
        event_manager.connect("message-destroy", self.on_message_destroy)
        self.add(self.control)
        self.reset_position()
        self.message_queue = deque()
        self.message_lock = Lock()
        self.is_through = True
        self.reset_position()                    
        self.hide_all()
        
    def on_message_coming(self, data):    
        if self.is_through:
            self.show_all()
            self.is_through = False
            
    def on_message_destroy(self, data):        
        if not self.control.has_messages:
           if not self.is_through: 
               self.hide_all()
               self.is_through = True
        
    def set_input_shape_mask(self, disable_input):    
        if disable_input:
            region = gtk.gdk.Region()
            self.window.input_shape_combine_region(region, 0, 0)
        else:    
            self.window.input_shape_combine_region(self.window.get_visible_region(), 0, 0)
        
    def reset_position(self):    
        screen_w, screen_h = get_screen_size()
        win_x = screen_w - WINDOW_WIDTH - WINDOW_OFFSET_WIDTH
        win_y = screen_h - WINDOW_HEIGHT - DOCK_HEIGHT - WINDOW_OFFSET_HEIGHT
        self.move(win_x, win_y)
    
    def on_notify_event(self, data):
        message_box = MinMessageBox(data)
        self.control.add_message_box(message_box)
        
    def on_expose_event(self, widget, event):    
        cr  = widget.window.cairo_create()
        rect = widget.allocation
        
        # Clear color to transparent window.
        if self.is_composited():
            cr.rectangle(*rect)
            cr.set_source_rgba(0, 0, 0, 0)
            cr.set_operator(cairo.OPERATOR_SOURCE)                
            cr.paint()
        else:    
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)            
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.set_source_rgb(0.9, 0.9, 0.9)
            cr.fill()
            
        propagate_expose(widget, event)        
        
        return True    
