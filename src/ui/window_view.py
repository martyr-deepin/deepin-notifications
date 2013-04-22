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
import cPickle

from dtk.ui.dialog import DialogBox, DIALOG_MASK_GLASS_PAGE
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.treeview import TreeView, TreeItem
from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_cairo
from ui.skin import app_theme
from notification_db import db
from events import event_manager

import pango


def draw_single_mask(cr, x, y, width, height, color_name):
    color = app_theme.get_color(color_name).get_color()
    cairo_color = color_hex_to_cairo(color)
    cr.set_source_rgb(*cairo_color)
    cr.rectangle(x, y, width, height)
    cr.fill()

TIME = 0
MESSAGE = 1
    
class BriefViewWindow(DialogBox):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        DialogBox.__init__(self, "MessageView", 370, 400, mask_type=DIALOG_MASK_GLASS_PAGE, close_callback=self.hide_all)
        
        self.items = []
        self.init_items_from_database()
        
        self.paged_items = {}
        self.page_count = 0
        self.page_index = "1"
        self.last_page_index = "-1"
        self.button_list = []
        
        self.pager()
        self.update_listview()

        self.init_button_box()  
        event_manager.connect("page-changed", self.on_page_changed)
        event_manager.emit("page-changed", None)
        
    def init_button_box(self):
        '''
        docs
        '''

        self.prev = Button("&lt;")
        self.next = Button("&gt;")
        self.prev.set_size_request(20, 20)
        self.next.set_size_request(20, 20)
        self.prev.connect("clicked", self.on_prev_clicked)
        self.next.connect("clicked", self.on_next_clicked)
        self.left_button_box.pack_start(self.prev, False, False, 1)
        self.left_button_box.pack_end(self.next, False, False, 0)
            
            
        i = 1
        while i <= self.page_count:
            b = Button(str(i))
            b.set_size_request(20, 20)
            b.connect("clicked", self.on_num_clicked)
            self.button_list.append(b)
            self.left_button_box.pack_start(b, False, False, 0)
            i += 1
            
    def on_num_clicked(self, widget):
        '''
        docs
        '''
        self.last_page_index = self.page_index
        self.page_index = widget.label
    
    
    def on_prev_clicked(self, widget):
        '''
        docs
        '''
        self.last_page_index = self.page_index
        self.page_index = str(int(self.page_index) - 1)
        event_manager.emit("page-changed", None)
    
    def on_next_clicked(self, widget):
        '''
        docs
        '''
        self.last_page_index = self.page_index
        self.page_index = str(int(self.page_index) + 1)

        event_manager.emit("page-changed", None)
    
            
    def on_page_changed(self, data):
        if self.page_index == "1":
            self.prev.set_sensitive(False)
        if self.page_index == str(self.page_count):
            self.next.set_sensitive(False)
        if self.last_page_index == "1":
            self.prev.set_sensitive(True)
        if self.last_page_index == str(self.page_count):
            self.next.set_sensitive(True)
            
        for b in self.button_list:
            if b.label == self.page_index:
                b.set_sensitive(False)
            if b.label == self.last_page_index:
                b.set_sensitive(True)
        
    def update_listview(self):
        '''
        docs
        '''
        items = self.paged_items[self.page_index]
        if hasattr(self, "listview"):
            del self.listview
        self.listview = TreeView(items)
        self.listview.set_expand_column(0)
        self.listview.set_column_titles(["The content of the message", "Time"],
                                        [self.sort_by_content, self.sort_by_time])
        
        self.body_box.pack_start(self.listview, False, False, 1)
        
        
    def init_items_from_database(self):
        '''
        docs
        '''
        message_list = db.get_all()

        for message in message_list:
            content = cPickle.loads(str(message[MESSAGE])).body
            time = message[TIME]
            item = BriefViewItem(content, time)
            self.items.append(item)
        
        if len(self.items) == 0:
            self.items.append(BriefViewItem("", ""))
        
    def pager(self):
        index = 1
        cursor = 1
        self.paged_items.clear()
        for item in self.items:
            if cursor > 6:
                index += 1
                cursor = 1
            self.paged_items.setdefault(str(index), []).append(item)
            cursor += 1
        self.page_count = index
        

    def sort_by_content(self, items, reverse):
        '''
        docs
        '''
        return sorted(items, key=lambda item : item.content, reverse=reverse)
        
    def sort_by_time(self, items, reverse):
        '''
        docs
        '''
        return sorted(items, key=lambda item : item.time, reverse=reverse)
        
        
class BriefViewItem(TreeItem):
    '''
    class docs
    '''
	
    def __init__(self, content, time):
        '''
        init docs
        '''
        TreeItem.__init__(self)
        self.content = content
        self.time = time
        self.item_height = 50
        self.content_width = 100
        self.time_width = 100
        self.draw_padding_x = 5
        self.column_index = 0
        self.is_select = False
        self.is_hover = False
        
    def get_height(self):    
        return self.item_height
    
    def get_column_widths(self):
        return [ self.content_width, self.time_width ]
    
    def get_column_renders(self):
        return (self.render_content, self.render_time)
    
    def unselect(self):
        self.is_select = False
        self.emit_redraw_request()
        
    def emit_redraw_request(self):    
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
            
    def select(self):        
        self.is_select = True
        self.emit_redraw_request()
        
    def render_content(self, cr, rect):        
        # Draw select background.
        if self.is_select:    
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemSelect")
        elif self.is_hover:
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
        
        if self.is_select:
            text_color = "#FFFFFF"
        else:    
            text_color = "#000000"
            
        draw_text(cr, self.content, rect.x + self.draw_padding_x,
                  rect.y, rect.width - self.draw_padding_x * 2, 
                  rect.height, text_size=10, 
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)    
        
    def render_time(self, cr, rect):    
        if self.is_select:    
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemSelect")
        elif self.is_hover:
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
        
        if self.is_select:
            text_color = "#FFFFFF"
        else:    
            text_color = "#000000"
            
        draw_text(cr, self.time, rect.x + self.draw_padding_x, 
                  rect.y, rect.width - self.draw_padding_x * 2,
                  rect.height, text_size=10, 
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)    
    
    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()
