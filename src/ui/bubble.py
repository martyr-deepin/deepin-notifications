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
from dtk.ui.draw import draw_pixbuf, draw_text, TEXT_ALIGN_TOP, TEXT_ALIGN_MIDDLE, TEXT_ALIGN_BOTTOM

from dtk.ui.utils import (propagate_expose, is_in_rect, get_content_size)
from events import event_manager
from ui.skin import app_theme
from ui.icons import icon_manager
from notification_db import db


WINDOW_OFFSET_WIDTH = 10
WINDOW_OFFSET_HEIGHT = 0
DOCK_HEIGHT = 35

TIMEOUT = 5000

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
	
    def __init__(self, message, height, create_time):
        '''
        init docs
        '''
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.message = message
        self.create_time = create_time
        self.init_size(height)
        self.init_pixbuf()
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rga_colormap())
        self.set_keep_above(True)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect("expose-event", self.on_expose_event)
        self.connect("button-press-event", self.on_button_press_event)
        self.connect("motion-notify-event", self.on_motion_notify_event)
        
        self.animation_time = 500
        self.level = 1
        self.win_x, self.win_y = self._get_position()
        self.win_y += self.window_height
        self.active_alpha = 1.0
        self.pointer_hand_rectangles = []
        
        self.fade_in_moving = False
        self.move_up_moving = False
        
        self.move(self.win_x, self.win_y)
        self.set_opacity(0)
        self.show_all()
        self.fade_in()
        self.timeout_id = gobject.timeout_add(TIMEOUT, self.start_destroy_animation)
        event_manager.connect("ready-to-move-up", self.move_up)
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

        
    def init_pixbuf(self):
        pixbuf_file_name = "mini.png" if self.window_height == 87 else "max.png"
        self.bg_pixbuf = app_theme.get_pixbuf(pixbuf_file_name).get_pixbuf()
        
        self.default_icon = app_theme.get_pixbuf("icon.png").get_pixbuf()
        self.message_icon = self.get_icon_pixbuf()
        
    
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
        self.draw_message(cr, rect)
        
        propagate_expose(widget, event)        
        
        return True
    
    def draw_message(self, cr, rect):
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
        
        #Draw body 
        body_text_y = SUMMARY_TEXT_Y + _height + TEXT_PADDING_Y
        render_hyperlink_support_text(self, cr, self.message.body, 
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
                action = self.message["hints"]["x-deepin-hyperlinks"][index]
                if action.has_key("href"):
                    webbrowser.open_new_tab(action.get("href"))
                return
    

    def _get_position(self):
        screen_w, screen_h = get_screen_size()
        win_x = screen_w - self.window_width - WINDOW_OFFSET_WIDTH
        win_y = screen_h - self.window_height - DOCK_HEIGHT - WINDOW_OFFSET_HEIGHT
        self.last_y = win_y
        return win_x, win_y
    
    def start_destroy_animation(self):
        timeline = Timeline(self.animation_time, CURVE_SINE)
        timeline.connect("update", lambda source, status : self.set_opacity(1 - status))
        timeline.connect("completed", lambda source : self.destroy)
        timeline.run()
        return False
    
    
    def move_up(self, move_up_height):
        
        if self.fade_in_moving:
            self.fade_in_timeline.stop()
            self.fade_in_complete(None)
        if self.move_up_moving:
            self.move_up_timeline.stop()
            self.move_up_completed(None)
            
        self.move_up_height = move_up_height
        self.move_up_moving = True
        self.move_up_timeline = Timeline(self.animation_time, CURVE_SINE)
        self.move_up_timeline.connect("update", 
                                      lambda source, status : self.move(self.win_x , self.win_y - int(self.move_up_height * status)))
        self.move_up_timeline.connect("completed", self.move_up_completed)
        self.move_up_timeline.run()
        
        
    def move_down(self, send_obj):
        db.remove(send_obj.create_time)
        if self.level == 2:
            (move_down_height) = send_obj.window_height
            self.move_up_timeline = Timeline(self.animation_time, CURVE_SINE)
            self.move_up_timeline.connect("update", 
                                          lambda source, status :
                                              self.move(self.win_x , self.win_y + int(move_down_height * status)))
            self.move_up_timeline.run()
        
    def move_up_completed(self, source):
        self.level += 1
        self.win_y -= self.move_up_height
        if self.level >= 3:
            gobject.source_remove(self.timeout_id)
            if self.get_opacity() > 0.5:
                self.start_destroy_animation()

        self.move_up_moving = False

    def fade_in(self):
        self.fade_in_moving = True
        
        def fade_in_step(status):
            self.move(self.win_x, self.win_y - int(self.window_height * status))
            if(status > 0.5):
                self.set_opacity(status)
            
        self.fade_in_timeline = Timeline(self.animation_time, CURVE_SINE)
        self.fade_in_timeline.connect("update", lambda source, status : fade_in_step(status))
        self.fade_in_timeline.connect("completed", self.fade_in_complete)
        self.fade_in_timeline.run()
        
    def fade_in_complete(self, source):
        '''
        docs
        '''
        self.win_y -= self.window_height
        self.fade_in_moving = False
