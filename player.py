import gi
import math
from gi.repository import Gtk

import services.bluetooth as bluetooth
from datetime import time

class PlayerWindow(Gtk.Container):
    def __init__(self, container):
        builder = Gtk.Builder()
        builder.add_from_file("be_player.glade")
        builder.connect_signals(self)

        self.player = builder.get_object("bluetooth_player")
        self.splashScreen = builder.get_object("no_media")
        self.song_title_label = builder.get_object("song_title")
        self.song_artist_label = builder.get_object("song_artist")
        self.song_duration_label = builder.get_object("song_duration")
        self.song_progress = builder.get_object("song_progress")
        self.song_duration = None

        self.btn_play = builder.get_object("btn_play")

        container.add(self.player)
        container.add(self.splashScreen)

        self.init_screen(builder, container)

        
    def init_screen(self, builder, window):
        def refresh_handler():
            self.init_screen(builder, window)

        try:
            bluetooth.load(self.on_song_update, refresh_handler)
            self.splashScreen.destroy()
            self.player.show_all()
        except bluetooth.NoMediaFound:
            self.splashScreen.show_all()
            self.player.hide()
  
    def on_btn_next_clicked(self, *args): 
        self.command(bluetooth.Command.NEXT)

    def on_btn_play_clicked(self, *args):
        if self.btn_play.get_label() == "gtk-media-pause":
            self.command(bluetooth.Command.PAUSE)
        else:    
            self.command(bluetooth.Command.PLAY)

    def on_btn_prev_clicked(self, *args):
        self.command(bluetooth.Command.PREVIOUS)

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

        if duration is not None and self.song_duration is not None:     
            self.song_duration_label.set_text("{} / {}".format(duration.strftime("%M:%S"), self.song_duration.strftime("%M:%S")))
            if (self.song_duration.microsecond + self.song_duration.second * 1000 + self.song_duration.minute * 60 * 1000) != 0:
                fraction = (duration.microsecond + duration.second * 1000 + duration.minute * 60 * 1000) / (self.song_duration.microsecond + self.song_duration.second * 1000 + self.song_duration.minute * 60 * 1000)
                self.song_progress.set_fraction(max(0, min(fraction, 1)))
            else:
                self.song_progress.set_fraction(0)

    def command(self, command):
        bluetooth.send_command(command)
        