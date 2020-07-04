import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from player import PlayerWindow


def on_main_window_destroy(*args):
    Gtk.main_quit()


builder = Gtk.Builder()
builder.add_from_file("main.glade")
builder.connect_signals({"on_main_window_destroy": Gtk.main_quit})

window = builder.get_object("main_window")
window.show_all()

be_player = PlayerWindow(builder.get_object("main_container"))
Gtk.main()