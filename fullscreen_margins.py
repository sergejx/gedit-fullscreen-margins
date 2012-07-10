# -*- coding: utf-8 -*-
#
#  fullscreen_margins.py (v0.1)
#    ~ Add margins around text in fullscreen mode, so lines are not too long.
#
#  Copyright (C) 2012 - Sergej Chodarev
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import gtk
import gtk.gdk
import gedit
import pango

class FullscreenMarginsPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = FullscreenMargins(window)

    def deactivate(self, window):
        self._instances[window].do_deactivate()
        del self._instances[window]

    def update_ui(self, window):
        self._instances[window].do_update_state()

class FullscreenMargins(object):

    def __init__(self, window):
        self.window = window
        self.margins = 0 # Currently used margins width
        self.do_activate()

    def do_activate(self):
        self.handlers = [
            self.window.connect("window-state-event", self.on_state_changed),
            self.window.connect("tab-added", self.on_tab_added)]

    def do_deactivate(self):
        # Remove event handelers
        for handler in self.handlers:
            self.window.disconnect(handler)
        # Remove margins
        if self.margins > 0:
            self.margins = 0
            self.set_all_margins()
        self.window = None

    def do_update_state(self):
        pass

    def on_state_changed(self, win, state):
        """React to change of window state."""
        if (state.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN):
            self.margins = self.compute_size()
            self.set_all_margins()
        else:
            if self.margins > 0:
                self.margins = 0
                self.set_all_margins()

    def on_tab_added(self, win, tab):
        """Set margins for new tabs."""
        if self.margins > 0:
            self.set_margins(tab.get_view())

    def get_char_width(self):
        """Try to get current default font and calculate character width."""
        try:
            view = self.window.get_active_view()
            # Get font description (code from "text size" plugin)
            context = view.get_style_context()
            description = context.get_font(context.get_state()).copy()
            # Get font metrics
            pango_context = view.get_pango_context()
            lang = pango_context.get_language()
            metrics = pango_context.get_metrics(description, lang)
            # Calculate char width in pixels
            width = metrics.get_approximate_char_width() / pango.SCALE
            return width
        except:
            return 8 # If it didn't work, just use some appropriate value

    def compute_size(self):
        """Compute optimal size of margins."""
        scr_width = self.window.get_screen().get_width()
        char_width = self.get_char_width()
        # Space for 80 chars + line numbers + scrollbar
        text_width = char_width * 86;
        margins = scr_width - text_width
        return int(margins / 2)

    def set_all_margins(self):
        """Set margins width to self.margins in all views."""
        for view in self.window.get_views():
            self.set_margins(view)

    def set_margins(self, view):
        """Set margins width to self.margins in a view."""
        margins = self.margins
        if margins < 2:
            margins = 2
        view.set_left_margin(margins)
        view.set_right_margin(margins)
