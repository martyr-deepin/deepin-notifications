#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
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
from threading import Thread

import gtk
import pango

from dtk.ui.menu import Menu
from dtk.ui.treeview import TreeView, TreeItem
from dtk.ui.dialog import ConfirmDialog
from dtk.ui.draw import draw_text
from dtk.ui.utils import is_in_rect, color_hex_to_cairo

from events import event_manager
from notification_db import db
from ui.utils import render_hyperlink_support_text, draw_single_mask
from nls import _

ID = 0
TIME = 1
MESSAGE = 2

class ListviewFactory(object):
    '''
    class docs
    '''
	
    def __init__(self, items, owner):
        '''
        init docs
        '''
        self.items = [ListViewItem(x, owner) for x in items]
        self.owner = owner
        self.count_per_page = 10 if self.owner == "brief" else 20
        self.listview = None
        
        self.page_count = 0
        self.page_index = 0
        self.paged_items = self.get_paged_items()
        
        self.init_listview()
        
    def prepend_item(self, item):
        if self.listview:
            self.listview.add_items([ListViewItem(item, self.owner)], insert_pos=0)
     
    def append_item(self, item):
        if self.listview:
            self.listview.add_items([ListViewItem(item, self.owner)])
        
    def on_listview_button_pressed(self, widget, event, listview):
        x = event.x
        y = event.y
        
        if event.button == 1:
            for item in listview.get_items():
                for index, rect in enumerate(item.pointer_hand_rectangles):
                    if is_in_rect((x, y), rect):
                        action = item.message["hints"]["x-deepin-hyperlinks"][index]
                        
                        if action.has_key("href"):
                            webbrowser.open_new_tab(action.get("href"))
                            
                            return
                        
            
    
    def on_listview_motion_notify(self, widget, event, listview):
        x = event.x
        y = event.y
        flag = False
        for item in listview.get_items():
            if flag:
                break
            for rect in item.pointer_hand_rectangles:
                if is_in_rect((x, y), rect):
                    flag = True
                    break
        if flag:
            widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
        else:
            widget.window.set_cursor(None)
         
        
    def init_listview(self):
        '''
        docs
        '''
        items = self.paged_items[self.page_index]

        self.listview = TreeView(items)
        self.listview.draw_mask = self.on_listview_draw_mask
        self.listview.set_expand_column(0)
        
        if self.owner == "detail":
            self.listview.set_column_titles([_("Content of messages"), _("Time")],
                                            [self.sort_by_content, self.sort_by_time])
        
        self.listview.draw_area.connect_after("button-press-event", self.on_listview_button_pressed, self.listview)
        self.listview.draw_area.connect_after("motion-notify-event", self.on_listview_motion_notify, self.listview)
        self.listview.connect("right-press-items", self.on_listview_right_press_items)
        self.listview.scrolled_window.connect("vscrollbar-state-changed", self.update_listview)
        
        event_manager.emit("listview-items-added", items)
        
    def update_listview(self, widget, state):
        if state == "bottom":
            if self.page_index < self.page_count - 1:
                self.page_index = self.page_index + 1
                
                items = self.paged_items[self.page_index]
                self.listview.add_items(items)
                
                event_manager.emit("listview-items-added", items)
                
    def on_listview_draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def on_listview_right_press_items(self, widget, root_x, root_y, current_item, select_items):
        if self.owner == "detail":        
            def on_delete_selected_record():
                def on_ok_clicked():
                    def _remove_selected():
                        for item in select_items:
                            db.remove(item.id)
                        db.commit()
                        widget.delete_items(select_items)
                        widget.get_toplevel()._init_data()
                    Thread(target=_remove_selected).run()
                
                dialog = ConfirmDialog(
                    _("Delete Item(s)"),
                    _("Are you sure you want to delete the selected item(s)?"),
                    confirm_callback = on_ok_clicked)
                dialog.show_all()
                
            def on_delete_all_record():
                def on_ok_clicked():
                    def _remove_all():
                        for item in self.items:
                            db.remove(item.id)
                        db.commit()
                        widget.get_toplevel().refresh_view()                        
                    Thread(target=_remove_all).run()

                dialog = ConfirmDialog(
                    _("Delete Item(s)"),
                    _("Are you sure delete all items?"),
                    confirm_callback = on_ok_clicked)
                dialog.show_all()
                
            Menu([(None, _("Delete selected item(s)"), on_delete_selected_record),
                  (None, _("Delete all items"), on_delete_all_record)], True).show((root_x, root_y))
        
    def get_paged_items(self):
        paged_items = {}
        
        index = 0
        for item in self.items:
            paged_items.setdefault(index / self.count_per_page, []).append(item)
            index += 1
            
        self.page_count = len(paged_items)
        return paged_items
        

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
    
    
        
def draw_half_rectangle(cr, rect, color, left_half=True):
    x, y, w, h = list(x for x in rect)
    cr.set_source_rgb(*color_hex_to_cairo(color))
    if left_half:
        cr.move_to(x + w + 1, y)
        cr.line_to(x, y)
        cr.line_to(x, y + h)
        cr.line_to(x + w, y + h)
        cr.stroke()
    else:
        cr.move_to(x, y)
        cr.line_to(x + w, y)
        cr.line_to(x + w, y + h)
        cr.line_to(x, y + h)
        cr.stroke()
    
    
class ListViewItem(TreeItem):
    '''
    class docs
    '''
	
    def __init__(self, data, owner):
        '''
        init docs
        '''
        TreeItem.__init__(self)
        
        self.id = data[ID]
        self.message = data[MESSAGE]
        self.content = self.message.body
        self.time = data[TIME]
        self.owner = owner
            
        self.item_height = 52
        self.content_width = 100
        self.time_width = 100 if self.owner == "detail" else 80
        self.draw_padding_x = 10
        self.draw_padding_y = 10
        self.column_index = 0
        self.is_select = False
        self.is_hover = False
        
        self.pointer_hand_rectangles = []
        
        
    def get_height(self):    
        return self.item_height

    def get_column_widths(self):
        return [ self.content_width, self.time_width ]
    
    def get_column_renders(self):
        return (self.render_content, self.render_time)
    
    def unselect(self):
        if self.owner == "detail":
            self.is_select = False
            self.emit_redraw_request()
        
    def emit_redraw_request(self):    
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
            
    def select(self):        
        if self.owner == "detail":
            self.is_select = True
            self.emit_redraw_request()
        
        
    def render_content(self, cr, rect):        
        if self.row_index % 2:
            cr.rectangle(*rect)
            cr.set_source_rgba(0, 0, 1, 0.05)
            cr.fill()
        
        # Draw select background.
        if self.owner == "detail":
            if self.is_select:    
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemSelect")
            elif self.is_hover:
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
                
            if self.is_select:
                text_color = "#FFFFFF"
            else:    
                text_color = "#000000"

        else:
            if self.is_hover:
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "#ebf4fd")
                draw_half_rectangle(cr, rect, "#7da2ce")
                
            text_color = "#000000"
                
            
        wrap_width = 25 * 10 if self.owner == "detail" else 20 * 10
        render_hyperlink_support_text(self, cr, self.content, 
                                      rect.x + self.draw_padding_x, 
                                      rect.y + self.draw_padding_y,
                                      rect.width - self.draw_padding_x * 2, 
                                      rect.height - self.draw_padding_y * 2, 
                                      wrap_width = wrap_width,
                                      clip_line_count = 2,
                                      text_color = text_color,
                                      alignment=pango.ALIGN_LEFT)    
        
    def render_time(self, cr, rect):    
        if self.row_index % 2:
            cr.rectangle(*rect)
            cr.set_source_rgba(0, 0, 1, 0.05)
            cr.fill()
        
        if self.owner == "detail":
            if self.is_select:    
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemSelect")
            elif self.is_hover:
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
                
            if self.is_select:
                text_color = "#FFFFFF"
            else:    
                text_color = "#000000"
                
        else:
            if self.is_hover:
                draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "#ebf4fd")
                draw_half_rectangle(cr, rect, "#7da2ce", False)
                
            text_color = "#000000"

        if self.owner == "detail":
            text = self.time.replace('-', ' ')
        else:
            text = self.time.split("-")[1][:-3]
            
        draw_text(cr, text, rect.x + 20,
                  rect.y + 10, rect.width,
                  rect.height / 2, 
                  text_color = text_color,
                  wrap_width = 50,
                  alignment=pango.ALIGN_CENTER)    
    
    
    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()
