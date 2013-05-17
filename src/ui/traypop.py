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

from dtk.ui.button import SwitchButton
from dtk.ui.label import Label
from dtk.ui.draw import draw_text, draw_hlinear
from dtk_cairo_blur import gaussian_blur
from dtk.ui.utils import (propagate_expose, color_hex_to_cairo, cairo_disable_antialias, is_in_rect, container_remove_all)


import gtk
import cairo
import pango
import gobject

from preference import preference
from ui.window_view import DetailWindow
from ui.skin import app_theme
from ui.listview_factory import ListviewFactory
from ui.utils import (root_coords_to_widget_coords, draw_round_rectangle_with_triangle)
from nls import _


ARROW_WIDHT = 10
ARROW_HEIGHT = 5
ROUND_RADIUS = 10

BORDER_LINE_WIDTH = 5
WINDOW_WIDHT = 300 + 2 * BORDER_LINE_WIDTH 
WINDOW_HEIGHT = 400 + 2 * BORDER_LINE_WIDTH

LIST_HEIGHT = 70
LIST_PADDING = 5
LIST_CONTENT_HEIGHT = 50
LIST_TIME_WIDTH = 100

COUNT_PER_PAGE = 2

FONT_SIZE = 10        
        
class SelectButton(gtk.Button):        
    def __init__(self, 
                 label="", 
                 bg_color="#ebf4fd",
                 line_color="#7da2ce"):
        gtk.Button.__init__(self)

        self.label = label
        self.bg_color = bg_color
        self.line_color = line_color
        self.text_color = "#000000"
        
        self.set_size_request(-1, 25)
                
        self.connect("expose-event", self.select_button_expose_event)        

        
    def select_button_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        if widget.state == gtk.STATE_PRELIGHT:
            with cairo_disable_antialias(cr):
                cr.set_source_rgb(*color_hex_to_cairo(self.bg_color))
                cr.rectangle(rect.x, 
                            rect.y, 
                            rect.width, 
                            rect.height)
                cr.fill()
        
                cr.set_source_rgb(*color_hex_to_cairo(self.line_color))
                cr.rectangle(rect.x,
                             rect.y, 
                             rect.width,
                             rect.height)
                cr.stroke()              
                
        # draw text.
        draw_text(cr, self.label,
                  rect.x, rect.y,
                  rect.width, rect.height,
                  text_size=FONT_SIZE, 
                  text_color=self.text_color,
                  alignment=pango.ALIGN_RIGHT
                  )        
        
        return True
    
    
class HSeparator(gtk.HBox):
	
    def __init__(self):
        gtk.HBox.__init__(self)
        
        self.connect("expose-event", self.on_expose_event)
        
    def on_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        draw_hlinear(cr, rect.x, rect.y + rect.height, rect.width, 1, [(0, ("#ffffff", 0)),
                                                                       (0.5, ("#2b2b2b", 0.5)), 
                                                                       (1, ("#ffffff", 0))])
        


class TrayPop(gtk.Window):
    '''
    class docs
    '''
	
    def __init__(self, x, y, items):
        '''
        init docs
        '''
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        
        self.x, self.y = x - WINDOW_WIDHT / 2, y - WINDOW_HEIGHT
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rgb_colormap())
        self.title_pixbuf = app_theme.get_pixbuf("icon_little.png").get_pixbuf()
        self.set_keep_above(True)
        self.set_size_request(WINDOW_WIDHT, WINDOW_HEIGHT)
        
        self.move(self.x, self.y)
        self.__init_view(items)
        
        self.connect("expose-event", self.on_expose_event)

        
    def __init_view(self, items):
        main_box = gtk.VBox()
        main_box_align = gtk.Alignment(1, 1, 1, 1)
        main_box_align.set_padding(10, 10, 10, 10)
        main_box_align.add(main_box)
        
        header_box = gtk.HBox()
        title_image = gtk.Image()
        title_image.set_from_pixbuf(self.title_pixbuf)
        title_label = Label(_("Unread Messages"), text_size=FONT_SIZE)
        title_switch = SwitchButton(not preference.disable_bubble)
        title_switch.set_tooltip_text(_("Close Notifications"))
        title_switch.connect("toggled", self.on_title_switch_toggled)
        header_box.pack_end(title_switch, False, False, 5)
        header_box.pack_start(title_image, False, False, 5)
        header_box.pack_start(title_label, False, False)
        
        self.body_box = gtk.VBox()
        self.listview_factory = ListviewFactory(items, "brief") if len(items) else None
        if self.listview_factory:
            self.body_align = gtk.Alignment(0.5, 0.5, 1, 1)
            self.body_align.set_padding(2, 2, 5, 5)
            self.body_align.add(self.listview_factory.listview)
        else:
            self.body_align = gtk.Alignment(0.5, 0.5, 0, 0)
            self.body_align.add(Label(_("(Empty)")))            
            
        self.body_box.pack_start(self.body_align, True, True)
        
        footer_box = gtk.HBox()
        button_more = SelectButton(_("More Advanced Options... "))
        button_more.connect("clicked", self.on_more_button_clicked)
        footer_box.pack_start(button_more, True, True)
        
        main_box.pack_start(header_box, False, False, 5)
        main_box.pack_start(HSeparator(), False, False, 5)
        main_box.pack_start(self.body_box, True, True)
        main_box.pack_end(footer_box, False, False, 5)        
        main_box.pack_end(HSeparator(), False, False, 5)

        self.add(main_box_align)
        
        
    def pointer_grab(self):
        gtk.gdk.pointer_grab(
            self.window,
            True,
            gtk.gdk.BUTTON_PRESS_MASK,
            None,
            None,
            gtk.gdk.CURRENT_TIME)
        
        gtk.gdk.keyboard_grab(
                self.window, 
                owner_events=False, 
                time=gtk.gdk.CURRENT_TIME)
        
        self.grab_add()
        self.connect("button-press-event", self.on_button_press)
        
    def pointer_ungrab(self):
        gtk.gdk.pointer_ungrab(gtk.gdk.CURRENT_TIME)
        gtk.gdk.keyboard_ungrab(gtk.gdk.CURRENT_TIME)
        self.grab_remove()
        
    def on_button_press(self, widget, event):
        ex, ey =  event.x_root, event.y_root
        
        win = widget.get_toplevel()
        x, y = win.get_position()
        tmp_x, tmp_y, w, h = win.allocation
        
        if not is_in_rect((ex, ey), (x, y, w, h)):
            self.dismiss()
            
    def on_title_switch_toggled(self, widget):
        if widget.get_active():
            preference.disable_bubble = False
        else:
            preference.disable_bubble = True

    def on_more_button_clicked(self, widget):
        DetailWindow().show_all()
        self.dismiss()
        
        
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
    
        
        # trayicon's location is relavant to root, but cairo need coordinates related to this widget.
        (self.x, self.y) = root_coords_to_widget_coords(self.x, self.y, self)
        
        
        # draw border and blur
        img_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WINDOW_WIDHT, WINDOW_HEIGHT)
        img_surf_cr = cairo.Context(img_surf)
        draw_round_rectangle_with_triangle(img_surf_cr, rect.x + BORDER_LINE_WIDTH, rect.y + BORDER_LINE_WIDTH,
                                           rect.width - 2 * BORDER_LINE_WIDTH, 
                                           rect.height - 2 * BORDER_LINE_WIDTH,
                                           ROUND_RADIUS, ARROW_WIDHT, ARROW_HEIGHT)
        
        img_surf_cr.set_line_width(1)
        img_surf_cr.stroke()
        gaussian_blur(img_surf, 2)
        
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_surface(img_surf, 0, 0)
        cr.rectangle(*rect)
        cr.fill()
        
        #draw content background
        draw_round_rectangle_with_triangle(cr, rect.x + BORDER_LINE_WIDTH, rect.y + BORDER_LINE_WIDTH,
                                           rect.width - 2 * BORDER_LINE_WIDTH, 
                                           rect.height - 2 * BORDER_LINE_WIDTH,
                                           ROUND_RADIUS, ARROW_WIDHT, ARROW_HEIGHT)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()

        
        propagate_expose(widget, event)
        
        return True
    
    def show_up(self):
        self.show_all()
        self.pointer_grab()
        
    def dismiss(self):
        self.destroy()
        self.pointer_ungrab()
    
gobject.type_register(TrayPop)    
