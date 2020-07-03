import gi
import math
from gi.repository import Gtk

import services.dbus_player as dbus
from datetime import time

class PlayerWindow(Gtk.Window):
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("main.glade")
        builder.connect_signals(self)
        
        window = builder.get_object("main_window")
        window.show_all()
        window.fullscreen()
        
        self.song_title_label = builder.get_object("song_title")
        self.song_artist_label = builder.get_object("song_artist")
        self.song_duration_label = builder.get_object("song_duration")
        self.song_progress = builder.get_object("song_progress")
        self.song_duration = None

        self.btn_play = builder.get_object("btn_play")
        
        dbus.load(self.on_song_update)

    def on_main_window_destroy(self, *args):
        Gtk.main_quit()

    def on_btn_next_clicked(self, *args): 
        self.command(dbus.Command.NEXT)

    def on_btn_play_clicked(self, *args):
        if self.btn_play.get_label() == "gtk-media-pause":
            self.command(dbus.Command.PAUSE)
        else:    
            self.command(dbus.Command.PLAY)

    def on_btn_prev_clicked(self, *args):
        self.command(dbus.Command.PREVIOUS)

    def on_song_update(self, song, playing, duration):
        if song is not None:
            self.song_title_label.set_text(song.title)
            self.song_artist_label.set_text(song.artist)

            self.song_duration = song.duration
            pass

        if playing is not None:
            if playing:
                self.btn_play.set_label("gtk-media-pause")
            else:
                self.btn_play.set_label("gtk-media-play")

        if duration is not None:     
            self.song_duration_label.set_text("{} / {}".format(duration.strftime("%M:%S"), self.song_duration.strftime("%M:%S")))
            
            fraction = (duration.microsecond + duration.second * 1000 + duration.minute * 60 * 1000) / (self.song_duration.microsecond + self.song_duration.second * 1000 + self.song_duration.minute * 60 * 1000)
            self.song_progress.set_fraction(max(0, min(fraction, 1)))

    def command(self, command):
        print("Sending command %s" % command)
        dbus.send_command(command)
        