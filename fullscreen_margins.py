# -*- coding: utf-8 -*-
#
#  fullscreen_margins.py (v1.1)
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

from gi.repository import Gdk, Gedit, GObject, Gtk, Pango

class FullscreenMargins(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "FullscreenMargins"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.margins = 0 # Currently used margins width

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

    def do_update_state(self):
        pass

    def on_state_changed(self, win, state):
        """React to change of window state."""
        if (state.new_window_state & Gdk.WindowState.FULLSCREEN):
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
            lang = Pango.Language.get_default()
            metrics = pango_context.get_metrics(description, lang)
            # Calculate char width in pixels
            width = metrics.get_approximate_char_width() / Pango.SCALE
            return width
        except:
            return 8 # If it didn't work, just use some appropriate value

    def compute_size(self):
        """Compute optimal size of margins."""
        # Get current monitor number
        screen = self.window.get_screen()
        monitor_n = screen.get_monitor_at_window(self.window.get_window())
        # and its width
        scr_width = screen.get_monitor_geometry(monitor_n).width
        # Get gutter width
        view = self.window.get_active_view()
        gutter_win = view.get_window(Gtk.TextWindowType.LEFT)
        gutter_width = gutter_win.get_width() if gutter_win else 0
        # Get scrollbar width
        scrollbar = view.get_parent().get_vscrollbar()
        scrollbar_width = scrollbar.get_allocated_width()
        # Calculate text width (use right_margin_position for column width)
        char_width = self.get_char_width()
        text_width = char_width * view.get_right_margin_position() + 4
        # Get sidepanel width
        sidepanel = self.window.get_side_panel()
        sidepanel_visible = sidepanel.get_visible()
        sidepanel_width = sidepanel.get_allocated_width() if sidepanel_visible else 0
        # Calculate margins
        margins = scr_width - text_width - gutter_width - scrollbar_width - sidepanel_width
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
