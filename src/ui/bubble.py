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

import gtk
import cairo
import gobject
import webbrowser

from ui.utils import get_screen_size, render_hyperlink_support_text
from dtk.ui.timeline import Timeline, CURVE_SINE
from dtk.ui.draw import draw_pixbuf, draw_text, TEXT_ALIGN_TOP
from dtk.ui.utils import (propagate_expose, is_in_rect, get_content_size)
from events import event_manager
from ui.skin import app_theme
from ui.icons import icon_manager
from deepin_utils.process import run_command

WINDOW_OFFSET_WIDTH = 10
WINDOW_OFFSET_HEIGHT = 0
DOCK_HEIGHT = 35

EXPIRE_TIMEOUT = 5000

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

class Bubble(gtk.Window):
    '''
    class docs
    '''
	
    def __init__(self, notification, height, create_time):
        '''
        init docs
        '''
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.notification = notification
        self.create_time = create_time
        self.init_size(height)
        self.init_pixbuf()
        
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rgb_colormap())
        self.set_keep_above(True)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)
        
        self.connect("expose-event", self.on_expose_event)
        self.connect("button-press-event", self.on_button_press_event)
        self.connect("motion-notify-event", self.on_motion_notify_event)
        
        self.animation_time = 200
        self.level = 1
        self.win_x, self.win_y = self._get_position()
        self.pointer_hand_rectangles = []
        
        self.move(self.win_x, self.win_y)
        self.set_opacity(0)
        self.show_all()
        self.timeout_id = gobject.timeout_add(EXPIRE_TIMEOUT, self.start_destroy_animation)
        
        event_manager.connect("manual-cancelled", self.move_down)
        
    def init_size(self, height):
        '''
        docs
        '''
        self.window_width = 302
        self.window_height = height
        
        self.close_pixbuf = app_theme.get_pixbuf("close.png").get_pixbuf()
        self.close_rect = gtk.gdk.Rectangle(self.window_width - self.close_pixbuf.get_width() - CLOSE_OFFSET_WIDTH,
                                            CLOSE_OFFSET_HEIGHT,
                                            self.close_pixbuf.get_width(),
                                            self.close_pixbuf.get_height())


        self.set_size_request(self.window_width, self.window_height)    
        
    @property
    def source_cmd(self):
        cmd = self.notification.hints.get("invoke")
        if cmd:
            return cmd
        
        return self.notification.app_name
        
    def get_icon_pixbuf(self):    
        hints = self.notification.hints
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
        
        app_icon = self.notification.app_icon
        if app_icon:
            pixbuf = icon_manager.pixbuf_from_icon_name(app_icon, ICON_SIZE[0])
            if pixbuf:    
                return pixbuf
            else:
                pixbuf = icon_manager.pixbuf_from_path(app_icon, ICON_SIZE[0], ICON_SIZE[1])
                if pixbuf:
                    return pixbuf
        
        return self.default_icon

        
    def init_pixbuf(self):
        pixbuf_file_name = "mini.png" if self.window_height == 87 else "max.png"
        self.bg_pixbuf = app_theme.get_pixbuf(pixbuf_file_name).get_pixbuf()
        
        self.default_icon = app_theme.get_pixbuf("icon.png").get_pixbuf()
        self.notification_icon = self.get_icon_pixbuf()
        
    
    def on_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        if self.is_composited():
            cr.rectangle(*rect)
            cr.set_source_rgba(0, 0, 0, 0)
            cr.set_operator(cairo.OPERATOR_SOURCE)                
            cr.fill()            
        else:    
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)            
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.set_source_rgb(0.9, 0.9, 0.9)
            cr.fill()
            

        cr.set_operator(cairo.OPERATOR_OVER)            
        self.draw_notification(cr, rect)
        
        propagate_expose(widget, event)        
        
        return True
    
    def draw_notification(self, cr, rect):
        draw_pixbuf(cr, self.bg_pixbuf, rect.x, rect.y)
        
        icon_x = rect.x + self.close_rect.x
        icon_y = rect.y + self.close_rect.y
        draw_pixbuf(cr, self.close_pixbuf, icon_x, icon_y)
        
        # Draw app icon.
        icon_x = APP_ICON_X + (APP_ICON_WIDTH  - self.notification_icon.get_width()) / 2
        icon_y = rect.y + (rect.height - self.notification_icon.get_height()) / 2
        draw_pixbuf(cr, self.notification_icon, icon_x, icon_y)
        
        # Draw summary.
        
        
        width, _height =  get_content_size(self.notification.summary)
        draw_text(cr, 
                  "<b>%s</b>" % self.notification.summary, 
                  rect.x + TEXT_X, rect.y + SUMMARY_TEXT_Y, 
                  TEXT_WIDTH - self.close_pixbuf.get_width(), _height,
                  text_color="#FFFFFF", text_size=10)
        
        #Draw body 
        body_text_y = SUMMARY_TEXT_Y + _height + TEXT_PADDING_Y
        render_hyperlink_support_text(self, cr, self.notification.body, 
                                      rect.x + TEXT_X, rect.y + body_text_y, 
                                      TEXT_WIDTH - self.close_pixbuf.get_width(),
                                      BODY_TEXT_HEIGHT,
                                      wrap_width=TEXT_WIDTH - self.close_pixbuf.get_width() + 5,
                                      text_color="#FFFFFF", text_size=10, 
                                      vertical_alignment=TEXT_ALIGN_TOP,
                                      clip_line_count=2)
        

    def on_motion_notify_event(self, widget, event):
        for rect in self.pointer_hand_rectangles:
            if is_in_rect((event.x, event.y), rect):
                widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                break
            else:
                widget.window.set_cursor(None)


            
    def on_button_press_event(self, widget, event):
        if is_in_rect((event.x, event.y), 
                      (self.close_rect.x, self.close_rect.y, 
                       self.close_rect.width, self.close_rect.height)):
            gobject.source_remove(self.timeout_id)
            self.destroy()
            event_manager.emit("manual-cancelled", self)
            return 
            
        for index, rect in enumerate(self.pointer_hand_rectangles):
            if is_in_rect((event.x, event.y), rect):
                action = self.notification["hints"]["x-deepin-hyperlinks"][index]
                if action.has_key("href"):
                    webbrowser.open_new_tab(action.get("href"))
                return
        
        rect = widget.allocation
        if is_in_rect((event.x, event.y),
                      (rect.x, rect.y, APP_ICON_WIDTH, self.window_height)):
            self.open_source_software()
    
    def open_source_software(self):
        run_command(self.source_cmd)

    def _get_position(self):
        screen_w, screen_h = get_screen_size()
        win_x = screen_w - self.window_width - WINDOW_OFFSET_WIDTH
        win_y = screen_h - self.window_height - DOCK_HEIGHT - WINDOW_OFFSET_HEIGHT
        self.last_y = win_y + self.window_height
        
        return win_x, win_y
    
    def start_destroy_animation(self):
        timeline = Timeline(self.animation_time, CURVE_SINE)
        timeline.connect("update", self.update_destory_animation)
        timeline.connect("completed", self.destroy_animation_complete)
        timeline.run()
        return False
    
    def update_destory_animation(self, source, status):
        if status != 1:
            self.set_opacity(1.0-status)
        else:
            self.destroy()
    
    def destroy_animation_complete(self, source):
        event_manager.emit("bubble-destroy", self)
        
    def move_up_by(self, move_up_height, update_height=False):
        self.win_y = int(self.last_y - move_up_height)
        self.move(self.win_x, self.win_y)
        if update_height:
            self.last_y = self.win_y
        
    def move_down_by(self, move_down_height, update_height=False):
        self.win_y = int(self.last_y + move_down_height)
        self.move(self.win_x, self.win_y)
        if update_height:
            self.last_y = self.win_y
        
    def move_down(self, send_obj):
        if self.level == 2:
            (move_down_height) = send_obj.window_height
            self.move_up_timeline = Timeline(self.animation_time, CURVE_SINE)
            self.move_up_timeline.connect("update", self.update_move_down_animation, move_down_height)
            self.move_up_timeline.run()
            
    def update_move_down_animation(self, source, status, move_down_height):
        self.move_down_by(move_down_height * status, not bool(status - 1))
