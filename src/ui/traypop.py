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

from dtk.ui.draw import draw_round_rectangle
from dtk.ui.utils import propagate_expose
from dtk.ui.label import Label
from dtk.ui.button import Button

import gtk
import cairo

#from ui.utils import root_coords_to_widget_coords

ARROW_WIDHT = 10
ARROW_HEIGHT = 5
WINDOW_WIDHT = 300
WINDOW_HEIGHT = 400

def root_coords_to_widget_coords(root_x, root_y, widget):
    (widget_x, widget_y) = widget.get_position()
    
    return (int(root_x - widget_x), int(root_y - widget_y))

class ViewFlipper(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        
        self.__init_data()
        self.__init_view()
        
        
    def __init_data(self):
        self.index = 1
        self.page = 1
        
        self.items = []
        self.paged_items = {}
        
    def __init_view(self):
        self.flipper_index = gtk.HBox()
        self.flipper_index.set_size_request(-1, 5)
        self.flipper_index.connect("expose-event", self.on_flipper_index_expose)
        
        self.content_box = gtk.VBox()
        self.main_view = gtk.HBox()
        self.left_button = Button("&lt;")
        self.right_button = Button("&gt;")
        self.main_view.pack_start(self.left_button, False, False, 1)
        self.main_view.pack_start(self.content_box)
        self.main_view.pack_start(self.right_button, False, False, 1)
        
        self.pack_start(self.flipper_index, False, False, 2)
        self.pack_start(self.main_view)
        

    def on_flipper_index_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        width_average = rect.width / self.page
        cr.rectangle(rect.x + (self.index - 1) * width_average, rect.y, width_average, rect.height)
        cr.set_source_rgb(0, 0, 1)
        cr.fill()
        
    def on_left_btn_clicked(self, widget):
        if self.index != 1:
            self.index -= 1
            self.update_view()
            
    def on_right_btn_clicked(self, widget):
        if self.index != self.page:
            self.index += 1
            self.update_view()
        
    def update_view(self):
        if self.index == 1:
            self.left_button.set_visible(False)
        else:
            self.left_button.set_visible(True)
            
        if self.index == self.page:
            self.right_button.set_visible(False)
        else:
            self.right_button.set_visible(True)
            
        
            

class TrayPop(gtk.Window):
    '''
    class docs
    '''
	
    def __init__(self, x, y):
        '''
        init docs
        '''
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        
        self.x, self.y = x, y
        self.set_size_request(WINDOW_WIDHT, WINDOW_HEIGHT)
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or gtk.gdk.Screen().get_rga_colormap())
        self.set_keep_above(True)
        
        self.move(x - WINDOW_WIDHT / 2, y - WINDOW_HEIGHT)
        self.__init_view()
        
        self.connect("expose-event", self.on_expose_event)
        
    def __init_view(self):
        main_box = gtk.VBox()
        main_box_align = gtk.Alignment(1, 1, 1, 1)
        main_box_align.set_padding(5, 5, 5, 5)
        main_box_align.add(main_box)
        
        header_box = gtk.HBox()
        title_label = Label("Message View")
        header_box.pack_start(title_label, False, False)
        main_box.pack_start(header_box, False, False, 5)
        main_box.pack_start(ViewFlipper())
        
        self.add(main_box_align)

    def on_expose_event(self, widget, event):
        '''
        docs
        '''
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        cr.set_source_rgb(1, 1, 1)        
        
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.rectangle(*rect)
        cr.fill()
    
        cr.set_operator(cairo.OPERATOR_SOURCE)
        draw_round_rectangle(cr, rect.x, rect.y, rect.width, rect.height - ARROW_HEIGHT, 10)
        cr.fill()
        
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
    
        

win = TrayPop(1000, 500)
win.show_all()
gtk.main()
