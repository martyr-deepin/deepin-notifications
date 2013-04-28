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
import re
import pango
import pangocairo

from dtk.ui.draw import draw_pixbuf, draw_text, TEXT_ALIGN_TOP, TEXT_ALIGN_MIDDLE, TEXT_ALIGN_BOTTOM
from dtk.ui.utils import cairo_state, color_hex_to_cairo, cairo_disable_antialias
from dtk.ui.constant import DEFAULT_FONT, DEFAULT_FONT_SIZE

from ui.skin import app_theme

def get_screen_size():
    root_window = gtk.gdk.get_default_root_window()
    return root_window.get_size()

def get_hyperlink_support_str(raw_str):
    result = {"result" : "", "actions" : []}
    
    def replace_hyper_with_underline(match_obj):
        action_key = match_obj.group(1)
        action_value = match_obj.group(2)
        if action_key == "href":
            action_value = action_value if action_value.startswith("http://") else "http://" + action_value
        result["actions"].append({action_key : action_value})
        return "<u>" + match_obj.group(3) + "</u>"
    
    regex = re.compile(r'<a\s+([^\s]+)\s*=\s*([^\s<>]+)\s*>([^<>\/].*?)</a>')
    
    result["result"] = regex.sub(replace_hyper_with_underline, raw_str)
    return result

def handle_message(message):
    hyperlink_support_str = get_hyperlink_support_str(message["body"])
    message["body"] = hyperlink_support_str["result"]
    message["hints"]["x-deepin-hyperlinks"] = hyperlink_support_str["actions"]
    return message

def render_hyperlink_support_text(obj, cr, markup, 
                                  x, y, w, h, 
                                  text_size=DEFAULT_FONT_SIZE, 
                                  text_color="#000000", 
                                  text_font=DEFAULT_FONT, 
                                  alignment=pango.ALIGN_LEFT,
                                  wrap_width=None, 
                                  underline=False,
                                  vertical_alignment=TEXT_ALIGN_MIDDLE,
                                  clip_line_count=None,
                                  ellipsize=pango.ELLIPSIZE_END,
                                  ):
    
    with cairo_state(cr):
        # Set color.
        cr.set_source_rgb(*color_hex_to_cairo(text_color))
    
        # Create pangocairo context.
        context = pangocairo.CairoContext(cr)
        
        # Set layout.
        layout = context.create_layout()
        layout.set_font_description(pango.FontDescription("%s %s" % (text_font, text_size)))
        layout.set_markup(markup)
        layout.set_alignment(alignment)
        if wrap_width == None:
            layout.set_single_paragraph_mode(True)
            layout.set_width(w * pango.SCALE)
            layout.set_ellipsize(ellipsize)
        else:
            layout.set_width(wrap_width * pango.SCALE)
            layout.set_wrap(pango.WRAP_WORD)
            
        (text_width, text_height) = layout.get_pixel_size()
        
        if underline:
            if alignment == pango.ALIGN_LEFT:
                cr.rectangle(x, y + text_height + (h - text_height) / 2, text_width, 1)
            elif alignment == pango.ALIGN_CENTER:
                cr.rectangle(x + (w - text_width) / 2, y + text_height + (h - text_height) / 2, text_width, 1)
            else:
                cr.rectangle(x + w - text_width, y + text_height + (h - text_height) / 2, text_width, 1)
            cr.fill()
            
        # Set render y coordinate.
        if vertical_alignment == TEXT_ALIGN_TOP:
            render_y = y
        elif vertical_alignment == TEXT_ALIGN_MIDDLE:
            render_y = y + max(0, (h - text_height) / 2)
        else:
            render_y = y + max(0, h - text_height)
            
        # Clip area.
        if clip_line_count:
            line_count = layout.get_line_count()
            if line_count > 0:
                line_height = text_height / line_count
                cr.rectangle(x, render_y, text_width, line_height * clip_line_count)
                cr.clip()
            
        # Draw text.
        cr.move_to(x, render_y)
        context.update_layout(layout)
        context.show_layout(layout)
        
        get_pointer_hand_rectangles(obj, markup, layout, x, render_y)
                    
def get_pointer_hand_rectangles(obj, text, pango_layout, render_x, render_y):
    u_start_index = []
    u_end_index = []
    start_index = 0
    end_index = 0
    
    record = 0
    while text.find("<u>", start_index) != -1 and text.find("</u>", end_index) != -1:
        start_index = text.find("<u>", start_index) + 1
        end_index = text.find("</u>", end_index) + 1
        
        start = start_index - record * (4 + 3)
        end = end_index - (record + 1) * 3 - record * 4
        
        u_start_index.append(start)
        u_end_index.append(end)
        record += 1
        
    i = 0
    while i < len(u_start_index):
        [x1, y1, width1, height1] = [x / pango.SCALE for x in pango_layout.index_to_pos(u_start_index[i])]
        [x2, y2, width2, height2] = [x / pango.SCALE for x in pango_layout.index_to_pos(u_end_index[i])]
        
        rect_x = x1 + render_x
        rect_y = y1 + render_y
        rect_width = x2 - x1 + width2
        rect_height = y2 - y1 + height2
        
        obj.pointer_hand_rectangles.append((rect_x, rect_y, rect_width, rect_height))
        i += 1

        
def draw_line(cr, start, end, color_name):
    if color_name.startswith("#"):
        color = color_name
    else:    
        color = app_theme.get_color(color_name).get_color()
    cairo_color = color_hex_to_cairo(color)        
    with cairo_disable_antialias(cr):
        cr.set_line_width(1)
        cr.set_source_rgb(*cairo_color)
        cr.move_to(*start)
        cr.line_to(*end)
        cr.stroke()

        
if __name__ == "__main__":
    raw_str = '''this is a test <a href="www.baidu.com">baidu</a>, another test <a href="www.google.com">google</a>'''
    print get_hyperlink_support_str(raw_str)
