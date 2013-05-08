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

import webbrowser

from dtk.ui.draw import draw_round_rectangle
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.draw import draw_text, draw_hlinear
from dtk.ui.utils import propagate_expose, color_hex_to_cairo, container_remove_all, is_in_rect, alpha_color_hex_to_cairo
from dtk.ui.popup_grab_window import PopupGrabWindow, wrap_grab_window


import gtk
import cairo
import pango

from ui.window_view import DetailViewWindow
from ui.utils import root_coords_to_widget_coords, render_hyperlink_support_text

ARROW_WIDHT = 10
ARROW_HEIGHT = 5
WINDOW_WIDHT = 300
WINDOW_HEIGHT = 400

LIST_HEIGHT = 70
LIST_PADDING = 5
LIST_CONTENT_HEIGHT = 50
LIST_TIME_WIDTH = 100

COUNT_PER_PAGE = 2

COLOR_BLUE = "#d2f9fe"

class ListItem(gtk.EventBox):
    '''
    class docs
    '''
	
    def __init__(self, message, time):
        '''
        init docs
        '''
        gtk.EventBox.__init__(self)
        self.set_visible_window(False)
        
        self.message = message
        self.time = time
        
        self.set_size_request(-1, LIST_HEIGHT)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK)
        
        self.pointer_hand_rectangles = []
        
        self.connect("expose-event", self.on_expose_event)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-press-event", self.on_button_press)
        
        
    def on_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.translate(rect.x, rect.y) # only the toplevel window has the gtk.gdk.window? all cr location is relative to it?
        
        draw_round_rectangle(cr, 0, 0, rect.width, rect.height, 5)
        cr.set_source_rgb(*color_hex_to_cairo(COLOR_BLUE))
        cr.fill()
        
        render_hyperlink_support_text(self, cr, self.message.body, 
                              0 + LIST_PADDING , 0,
                              rect.width - LIST_PADDING * 2, LIST_CONTENT_HEIGHT,
                              wrap_width = rect.width - LIST_PADDING * 2,
                              clip_line_count = 3,
                              alignment=pango.ALIGN_LEFT)    
        
        draw_hlinear(cr, 0, 0 + LIST_CONTENT_HEIGHT, rect.width, 1, [(0, ("#ffffff", 0)),
                                                                               (0.5, ("#2b2b2b", 0.5)), 
                                                                               (1, ("#ffffff", 0))])
        
        time = self.time.split("-")[1]
        draw_text(cr, time, 0 + LIST_PADDING, 
                  0 + LIST_CONTENT_HEIGHT , LIST_TIME_WIDTH, rect.height - LIST_CONTENT_HEIGHT)
        
    def on_motion_notify(self, widget, event):
        '''
        docs
        '''
        x = event.x
        y = event.y
        flag = False
        
        
        for rect in self.pointer_hand_rectangles:
            if is_in_rect((x, y), rect):
                flag = True
                break
            
        if flag:
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
        else:
            widget.window.set_cursor(None)

            
    def on_button_press(self, widget, event):
        x = event.x
        y = event.y
        
        if event.button == 1:
            for index, rect in enumerate(self.pointer_hand_rectangles):
                if is_in_rect((x, y), rect):
                    action = self.message["hints"]["x-deepin-hyperlinks"][index]
                    
                    if action.has_key("href"):
                        webbrowser.open_new_tab(action.get("href"))
                        
                        return

    


class ViewFlipper(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, items):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        
        self.__init_data(items)
        self.__init_view()
        
        
    def __init_data(self, items):
        self.items = items
        self.paged_items = {}
        
        self.index = 1
        self.page_count = 1
        
        index = 0
        for item in self.items:
            self.paged_items.setdefault(index / COUNT_PER_PAGE + 1, []).append(item)
            index += 1
            
        self.page_count = len(self.paged_items) or 1
        
        
    def __init_view(self):
        self.flipper_index = gtk.HBox()
        self.flipper_index.set_size_request(-1, 5)
        self.flipper_index.connect("expose-event", self.on_flipper_index_expose)
        
        self.content_box = gtk.VBox()
        
        if len(self.paged_items) != 0:
            for item in self.paged_items[self.index]:
                self.content_box.pack_start(ListItem(*item), False, False, 2)
        else:
            align = gtk.Alignment(0.5, 0.5, 0, 0)
            align.add(Label("(Empty)"))
            self.content_box.pack_start(align)
        
        self.pack_start(self.flipper_index, False, False, 2)
        self.pack_start(self.content_box)
        

    def on_flipper_index_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        width_average = rect.width / self.page_count
        cr.rectangle(rect.x + (self.index - 1) * width_average, rect.y, width_average, rect.height)
        cr.set_source_rgb(0, 0, 1)
        cr.fill()
        
    def flip_forward(self):
        if self.index != self.page_count:
            self.index += 1
            self.update_view()
            
    def flip_backward(self):
        if self.index != 1:
            self.index -= 1
            self.update_view()
        
    def update_view(self):
        self.flipper_index.queue_draw()
        
        container_remove_all(self.content_box)
        for item in self.paged_items[self.index]:
            self.content_box.pack_start(ListItem(*item), False, False, 2)
        self.content_box.show_all()
        
        



class TrayPop(gtk.Window):
    '''
    class docs
    '''
	
    def __init__(self, x, y, items):
        '''
        init docs
        '''
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        
        self.x, self.y = x, y
        self.set_size_request(WINDOW_WIDHT, WINDOW_HEIGHT)
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rga_colormap())
        self.set_keep_above(True)
        
        self.move(x - WINDOW_WIDHT / 2, y - WINDOW_HEIGHT)
        self.__init_view(items)
        
        self.connect("expose-event", self.on_expose_event)
        
        wrap_grab_window(pop_tray_window, self)
        
    def __init_view(self, items):
        main_box = gtk.VBox()
        main_box_align = gtk.Alignment(1, 1, 1, 1)
        main_box_align.set_padding(5, 5, 5, 5)
        main_box_align.add(main_box)
        
        header_box = gtk.HBox()
        title_label = Label("Message View")
        header_box.pack_start(title_label, False, False)
        
        self.view_flipper = ViewFlipper(items)
        self.flipper_align = gtk.Alignment(0.5, 0.5, 1, 1)
        self.flipper_align.connect("expose-event", self.on_flipper_align_expose)
        self.flipper_align.set_padding(5, 5, 10, 10)
        self.flipper_align.add(self.view_flipper)
        
        self.on_open_message_manager()
        
        footer_box = gtk.HBox()
        self.left_button = Button("&lt;")
        self.left_button.set_size_request(50, 20)
        self.left_button.connect("clicked", self.on_left_btn_clicked)
        self.right_button = Button("&gt;")
        self.right_button.set_size_request(50, 20)
        self.right_button.connect("clicked", self.on_right_btn_clicked)        

        footer_box.pack_start(self.left_button, False, False, 5)
        footer_box.pack_end(self.right_button, False, False, 5)
        
        main_box.pack_start(header_box, False, False, 5)
        main_box.pack_start(self.flipper_align)
        main_box.pack_end(footer_box, False, False, 5)
        
        self.add(main_box_align)
        
        
    def on_flipper_align_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        draw_hlinear(cr, rect.x, rect.y + rect.height, rect.width, 1, [(0, ("#ffffff", 0)),
                                                                       (0.5, ("#2b2b2b", 0.5)), 
                                                                       (1, ("#ffffff", 0))])

    def on_open_message_manager(self):
        DetailViewWindow().show_all()
        
    def on_left_btn_clicked(self, widget):
        self.view_flipper.flip_backward()
    
    
    def on_right_btn_clicked(self, widget):
        self.view_flipper.flip_forward()
    

    def on_expose_event(self, widget, event):
        '''
        docs
        '''
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.rectangle(*rect)
        cr.fill()
    
        cr.set_operator(cairo.OPERATOR_SOURCE)
        draw_round_rectangle(cr, rect.x, rect.y, rect.width, rect.height - ARROW_HEIGHT, 10)
        cr.set_source_rgb(1, 1, 1)   
        cr.fill()
        
        #draw alpha border to realize the effect like background blur
        draw_round_rectangle(cr, rect.x, rect.y, rect.width, rect.height - ARROW_HEIGHT, 10)
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#b2b2b2", 0.5)))
        cr.set_line_width(3)
        cr.stroke()
        
        
        # trayicon's location is relavant to root, but cairo need coordinates related to this widget.
        (self.x, self.y) = root_coords_to_widget_coords(self.x, self.y, self)

        cr.set_source_rgb(1, 1, 1)
        cr.move_to(self.x + 50 , self.y + 50)
        cr.line_to(self.x - ARROW_WIDHT / 2, self.y - ARROW_HEIGHT)
        cr.line_to(self.x + ARROW_WIDHT / 2, self.y - ARROW_HEIGHT)
        cr.line_to(self.x, self.y)
        cr.close_path()        
        cr.fill()

        propagate_expose(widget, event)
        
        return True
    
    
pop_tray_window = PopupGrabWindow(TrayPop)        
