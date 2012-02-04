from gi.repository import GObject, Gedit, Gdk, Pango

class FullscreenMarginsWindowActivatable(GObject.Object,
                                         Gedit.WindowActivatable):
    __gtype_name__ = "FullscreenMarginsWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.margins = 0 # Currently used margins width

    def do_activate(self):
        self.state_handler = self.window.connect("window-state-event",
                                                 self.on_state_changed)
        self.tab_handler = self.window.connect("tab-added", self.on_tab_added)

    def do_deactivate(self):
        self.window.disconnect(self.state_handler)
        self.window.disconnect(self.tab_handler)

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
        view.set_right_margin(self.margins)
        view.set_left_margin(self.margins)
