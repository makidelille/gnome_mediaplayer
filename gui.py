import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from player import PlayerWindow

win = PlayerWindow()
Gtk.main()