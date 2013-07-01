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

"""
    Provides methods for convenient icons and image handling
"""

import cairo
import glib
import gtk

def get_optimum_pixbuf(filepath, expect_width, expect_height, cut_middle_area=True):
    '''
    Get optimum size pixbuf from file.
    
    @param filepath: Filepath to contain image.
    @param expect_width: Expect width.
    @param expect_height: Expect height.
    @param cut_middle_area: Default cut image with middle area.
    @return: Return optimum size pixbuf with expect size.
    '''
    
    if not isinstance(filepath, gtk.gdk.Pixbuf):
        pixbuf = gtk.gdk.pixbuf_new_from_file(filepath)
    else:    
        pixbuf = filepath
        
    pixbuf_width, pixbuf_height = pixbuf.get_width(), pixbuf.get_height()
    if pixbuf_width >= expect_width and pixbuf_height >= expect_height:
        if float(pixbuf_width) / pixbuf_height == float(expect_width) / expect_height:
            scale_width, scale_height = expect_width, expect_height
        elif float(pixbuf_width) / pixbuf_height > float(expect_width) / expect_height:
            scale_height = expect_height
            scale_width = int(float(pixbuf_width) * expect_height / pixbuf_height)
        else:
            scale_width = expect_width
            scale_height = int(float(pixbuf_height) * expect_width / pixbuf_width)
            
        if cut_middle_area:
            subpixbuf_x = (scale_width - expect_width) / 2
            subpixbuf_y = (scale_height - expect_height) / 2
        else:
            subpixbuf_x = 0
            subpixbuf_y = 0
            
        return pixbuf.scale_simple(
            scale_width, 
            scale_height, 
            gtk.gdk.INTERP_BILINEAR).subpixbuf(subpixbuf_x,
                                               subpixbuf_y,
                                               expect_width, 
                                               expect_height)
    elif pixbuf_width >= expect_width:
        scale_width = expect_width
        scale_height = int(float(expect_width) * pixbuf_height / pixbuf_width)
        
        if cut_middle_area:
            subpixbuf_x = (scale_width - expect_width) / 2
            subpixbuf_y = max((scale_height - expect_height) / 2, 0)
        else:
            subpixbuf_x = 0
            subpixbuf_y = 0
            
        return pixbuf.scale_simple(
            scale_width,
            scale_height,
            gtk.gdk.INTERP_BILINEAR).subpixbuf(subpixbuf_x,
                                               subpixbuf_y,
                                               expect_width, 
                                               min(expect_height, scale_height))
    elif pixbuf_height >= expect_height:
        scale_width = int(float(expect_height) * pixbuf_width / pixbuf_height)
        scale_height = expect_height
        
        if cut_middle_area:
            subpixbuf_x = max((scale_width - expect_width) / 2, 0)
            subpixbuf_y = (scale_height - expect_height) / 2
        else:
            subpixbuf_x = 0
            subpixbuf_y = 0
        
        return pixbuf.scale_simple(
            scale_width,
            scale_height,
            gtk.gdk.INTERP_BILINEAR).subpixbuf(subpixbuf_x,
                                               subpixbuf_y,
                                               min(expect_width, scale_width), 
                                               expect_height)
    else:
        return pixbuf

class IconManager(object):
    """
        Provides convenience functions for
        managing icons and images in general
    """
    def __init__(self):
        self.icon_theme = gtk.icon_theme_get_default()
        self.icon_factory = gtk.IconFactory()
        self.icon_factory.add_default()
        # Any arbitrary widget is fine
        self.system_visual = gtk.gdk.visual_get_system()
        self.system_colormap = gtk.gdk.colormap_get_system()
        
        # TODO: Make svg actually recognized
        self._sizes = [16, 22, 24, 32, 48, 'scalable']
        self._cache = {}

    def pixbuf_from_icon_name(self, icon_name, size=48):
        """
            Generates a pixbuf from an icon name

            :param stock_id: an icon name
            :type stock_id: string
            :param size: the size of the icon, will be
                tried to converted to a GTK icon size
            :type size: int or GtkIconSize

            :returns: the generated pixbuf
            :rtype: :class:`gtk.gdk.Pixbuf` or None
        """
        if type(size) == gtk.IconSize:
            icon_size = gtk.icon_size_lookup(size)
            size = icon_size[0]

        try:
            pixbuf = self.icon_theme.load_icon(
                icon_name, size, gtk.ICON_LOOKUP_NO_SVG)
        except glib.GError as e:
            print e
            pixbuf = None

        # TODO: Check if fallbacks are necessary
        return pixbuf
    
    def pixbuf_from_dbus(self, array, size=None):
        if len(array) != 7:
            return None
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_data(data="".join(chr(i) for i in array[-1]), 
                                                  colorspace=gtk.gdk.COLORSPACE_RGB,
                                                  has_alpha=array[3], 
                                                  bits_per_sample=array[4],
                                                  width=array[0], 
                                                  height=array[1], 
                                                  rowstride=array[2])
        except:    
            return None
        else:    
            if size:
                pixbuf = get_optimum_pixbuf(pixbuf, size[0], size[1])
            return pixbuf
        
    def pixbuf_from_path(self, file_path, x, y):    
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(file_path)
        except:
            return None
        else:
            return get_optimum_pixbuf(pixbuf, x, y)
        
    
    def pixbuf_from_data(self, data, size=None, keep_ratio=True, upscale=False):
        """
            Generates a pixbuf from arbitrary image data

            :param data: The raw image data
            :type data: byte
            :param size: Size to scale to; if not specified,
                the image will render to its native size
            :type size: tuple of int
            :param keep_ratio: Whether to keep the original
                image ratio on resizing operations
            :type keep_ratio: bool
            :param upscale: Whether to upscale if the requested
                size exceeds the native size
            :type upscale: bool

            :returns: the generated pixbuf
            :rtype: :class:`gtk.gdk.Pixbuf` or None
        """
        if not data:
            return None

        pixbuf = None
        loader = gtk.gdk.PixbufLoader()

        if size is not None:
            def on_size_prepared(loader, width, height):
                """
                    Keeps the ratio if requested
                """
                if keep_ratio:
                    scale = min(size[0] / float(width), size[1] / float(height))

                    if scale > 1.0 and upscale:
                        width = int(width * scale)
                        height = int(height * scale)
                    elif scale <= 1.0:
                        width = int(width * scale)
                        height = int(height * scale)
                else:
                    if upscale:
                        width, height = size
                    else:
                        width = height = max(width, height)

                loader.set_size(width, height)
            loader.connect('size-prepared', on_size_prepared)

        try:
            loader.write(data)
            loader.close()
        except glib.GError as e:
            print e
        else:
            pixbuf = loader.get_pixbuf()

        return pixbuf

    def pixbuf_from_text(self, text, size, background_color='#456eac',
            border_color='#000', text_color='#fff'):
        """
            Generates a pixbuf based on a text, width and height

            :param size: A tuple describing width and height
            :type size: tuple of int
            :param background_color: The color of the background as
                hexadecimal value
            :type background_color: string
            :param border_color: The color of the border as
                hexadecimal value
            :type border_color: string
            :param text_color: The color of the text as
                hexadecimal value
            :type text_color: string
        """
        pixmap_width, pixmap_height = size
        key = '%s - %sx%s - %s' % (text, pixmap_width, pixmap_height,
            background_color)
        
        if self._cache.has_key(key):
            return self._cache[key]

        pixmap = gtk.gdk.Pixmap(None, pixmap_width, pixmap_height,
            self.system_visual.depth)
        context = pixmap.cairo_create()

        context.set_source_color(gtk.gdk.Color(background_color))
        context.set_line_width(1)
        context.rectangle(1, 1, pixmap_width - 2, pixmap_height - 2)
        context.fill()

        context.set_source_color(gtk.gdk.Color(text_color))
        context.select_font_face('sans-serif 10')
        x_bearing, y_bearing, width, height = context.text_extents(text)[:4]
        x = pixmap_width / 2 - width / 2 - x_bearing
        y = pixmap_height / 2 - height / 2 - y_bearing
        context.move_to(x, y)
        context.show_text(text)

        context.set_source_color(gtk.gdk.Color(border_color))
        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.rectangle(0, 0, pixmap_width - 1, pixmap_height - 1)
        context.stroke()

        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
            pixmap_width, pixmap_height)
        pixbuf = pixbuf.get_from_drawable(pixmap, self.system_colormap,
            0, 0, 0, 0, pixmap_width, pixmap_height)

        self._cache[key] = pixbuf

        return pixbuf


icon_manager = IconManager()    
