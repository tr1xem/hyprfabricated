import random
from fabric.utils import get_relative_path
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.stack import Stack
from fabric.widgets.image import Image
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GObject

from modules.widgets import Widgets
from modules.pins import Pins
from modules.wallpapers import WallpaperSelector
from modules.kanban import Kanban

class Dashboard(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="dashboard",
            orientation="v",
            spacing=8,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            visible=True,
            all_visible=True,
        )

        self.notch = kwargs["notch"]
        
        # Create main container
        self.main_box = Box(
            orientation="v",
            spacing=8,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )
        
        # Set minimum size on main_box directly
        self.main_box.set_size_request(1033, 400)
        
        # Initialize widgets first
        self.widgets = Widgets(notch=self.notch)
        self.pins = Pins()
        self.kanban = Kanban()
        self.wallpapers = WallpaperSelector()
        
        # Create stack
        self.stack = Stack(
            name="stack",
            transition_type="slide-left-right",
            transition_duration=500,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )
        
        # Create switcher after stack
        self.switcher = Gtk.StackSwitcher(
            name="switcher",
            spacing=8,
        )
        self.switcher.set_stack(self.stack)
        self.switcher.set_hexpand(True)
        self.switcher.set_vexpand(False)
        self.switcher.set_halign(Gtk.Align.FILL)
        self.switcher.set_valign(Gtk.Align.START)
        self.switcher.set_homogeneous(True)

        # Create coming soon page
        self.coming_soon_start_label = Label(
            name="coming-soon-label",
            label="I need...",
            justification="center",
        )
        self.coming_soon_end_label = Label(
            name="coming-soon-label",
            label="To sleep...",
            justification="center",
        )

        self.soon = Image(
            name="coming-soon",
            pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_scale(
                get_relative_path("../assets/soon.png"), 366, 300, True
            ),
        )

        self.coming_soon = Box(
            name="coming-soon",
            orientation="v",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            spacing=8,
            children=[
                Box(
                    h_align="fill",
                    v_align="fill",
                    h_expand=True,
                    v_expand=True,
                    children=[self.coming_soon_start_label],
                ),
                self.soon,
                Box(
                    h_align="fill",
                    v_align="fill",
                    h_expand=True,
                    v_expand=True,
                    children=[self.coming_soon_end_label],
                ),
            ],
        )

        # Add pages to stack
        self.stack.add_titled(self.widgets, "widgets", "Widgets")
        self.stack.add_titled(self.pins, "pins", "Pins")
        self.stack.add_titled(self.kanban, "kanban", "Kanban")
        self.stack.add_titled(self.wallpapers, "wallpapers", "Wallpapers")
        self.stack.add_titled(self.coming_soon, "coming-soon", "Coming soon...")

        # Build widget hierarchy
        self.main_box.pack_start(self.switcher, False, True, 0)
        self.main_box.pack_start(self.stack, True, True, 0)
        self.add(self.main_box)

        # Connect visible-child signal after stack is fully set up
        self.stack.connect("notify::visible-child", self.on_visible_child_changed)
        
        self.show_all()

    def go_to_next_child(self):
        children = self.stack.get_children()
        current_index = self.get_current_index(children)
        next_index = (current_index + 1) % len(children)
        self.stack.set_visible_child(children[next_index])

    def go_to_previous_child(self):
        children = self.stack.get_children()
        current_index = self.get_current_index(children)
        previous_index = (current_index - 1 + len(children)) % len(children)
        self.stack.set_visible_child(children[previous_index])

    def get_current_index(self, children):
        current_child = self.stack.get_visible_child()
        return children.index(current_child) if current_child in children else -1

    def on_visible_child_changed(self, stack, param):
        visible = stack.get_visible_child()
        if visible == self.wallpapers:
            self.wallpapers.search_entry.set_text("")
            self.wallpapers.search_entry.grab_focus()
        if visible == self.coming_soon:
            # Define paired messages for the coming_soon widget using tuples
            text_pairs = (
                ("I need...", "To sleep..."),
                ("Another day...", " Another bug..."),
                ("I really need...", "An energy drink..."),
                ("7 minutes without ricing...", "TIME TO CODE!"),
                ("git commit... git p-", "tf is a merge?"),
                ("This should work...", "Why doesn't it work?"),
                ("Just one more line...", "8 hours later..."),
                ("Hello world...", "Segfault."),
                ("I'll fix that later...", "Technical debt intensifies."),
                ("sudo rm -rf /", "Wait, NO—"),
                ("Almost done...", "SyntaxError: unexpected EOF"),
                ("AI will take our jobs...", "Meanwhile: writing regex."),
                ("Arch is unstable!", "3 years, no reinstall."),
                ('printf("Hello world");', "Where is my semicolon?"),
                ("I'll sleep early today...", "3AM: still debugging."),
                ("Oh, a tiny bug...", "Refactoring the whole codebase."),
                ("rm -rf node_modules", "Project reborn."),
                ("Pipenv, poetry, venv...", "Which one was I using?"),
            )

            new_start_text, new_end_text = random.choice(text_pairs)
            self.coming_soon_start_label.set_text(new_start_text)
            self.coming_soon_end_label.set_text(new_end_text)

    def go_to_section(self, section_name):
        """Navigate to a specific section in the dashboard."""
        if section_name == "widgets":
            self.stack.set_visible_child(self.widgets)
        elif section_name == "pins":
            self.stack.set_visible_child(self.pins)
        elif section_name == "kanban":
            self.stack.set_visible_child(self.kanban)
        elif section_name == "wallpapers":
            self.stack.set_visible_child(self.wallpapers)
        elif section_name == "coming-soon":
            self.stack.set_visible_child(self.coming_soon)
