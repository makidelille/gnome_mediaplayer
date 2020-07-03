import dbus, dbus.mainloop.glib, sys
from gi.repository import GLib
from enum import Enum
from datetime import time


class Command(Enum):
    PLAY = "play"
    PAUSE = "pause"
    NEXT = "next"
    PREVIOUS = "previous"
    VOLUME = "volume"

class NoMediaFound(Exception):
    pass

class NoTransportFound(Exception):
    pass

class Song(object):
    title  = None
    artist = None
    album  = None
    duration = None

    def __init__(self, title, artist, album, duration):
        self.title = title.decode("utf-8")
        self.artist = artist.decode("utf-8")
        self.album  = album.decode("utf-8")
        self.duration = duration
    
    def __eq__(self, other):
        if isinstance(other, Song):
            return self.title == other.title and self.artist == other.artist and self.album == other.album and self.duration == other.duration
        return False

def millisToTime(millis):
    return time(
        microsecond=millis%1000,
        second=(millis//1000)%60,
        minute=(millis//(1000*60))%60,
        hour=(millis//(1000*60*60))%24,
    )


player_iface = None
transport_prop_iface = None

def load(callback):
    gui_handler = generateCallback(callback)

    global player_iface
    global transport_prop_iface
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    obj = bus.get_object('org.bluez', "/")
    mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
    for path, ifaces in mgr.GetManagedObjects().items():
        if 'org.bluez.MediaPlayer1' in ifaces:
            player_iface = dbus.Interface(
                    bus.get_object('org.bluez', path),
                    'org.bluez.MediaPlayer1')

            current_media = dbus.Interface(bus.get_object('org.bluez', path), 'org.freedesktop.DBus.Properties')
            current_properties = current_media.GetAll('org.bluez.MediaPlayer1')
            print(current_properties)
            gui_handler('org.bluez.MediaPlayer1', current_properties, False)
        elif 'org.bluez.MediaTransport1' in ifaces:
            transport_prop_iface = dbus.Interface(
                    bus.get_object('org.bluez', path),
                    'org.freedesktop.DBus.Properties')
    if not player_iface:
        raise NoMediaFound('Error: Media Player not found.') 
    if not transport_prop_iface:
        raise NoTransportFound('Error: DBus.Properties iface not found.') 
    
    bus.add_signal_receiver(
        gui_handler,
        bus_name='org.bluez',
        signal_name='PropertiesChanged',
        dbus_interface='org.freedesktop.DBus.Properties')

    ## on lit les propriété courrante du mediaplayer

def generateCallback(callback):
    def handler(interface, changed, invalidated):
        if interface != 'org.bluez.MediaPlayer1':
            return
        else:
            playing = None
            song = None
            position = None

            for prop, value in changed.items():
                if prop == 'Status':
                    playing = value == "playing"
                elif prop == 'Track':
                    song = Song(
                        title = value.get('Title', '').encode('utf-8'),
                        artist = value.get('Artist', '').encode('utf-8'),
                        album = value.get('Album', '').encode('utf-8'),
                        duration = millisToTime(value.get('Duration', ''))
                    )
                elif prop == 'Position':
                    position = millisToTime(value)
                else:
                    print('unknown Prop {} : {}'.format(prop, value))
            callback(song, playing, position)
    return handler   

def send_command(command, vol = -1):
    if player_iface is None:
        raise NoMediaFound('Error: Media Player not found.') 

    if command == Command.PLAY:
        player_iface.Play()
    elif command == Command.PAUSE:
        player_iface.Pause()
    elif command == Command.NEXT:
        player_iface.Next()
    elif command == Command.PREVIOUS:
        player_iface.Previous()
    elif command == Command.VOLUME:
        if vol not in range(0, 128):
            print('Possible Values: 0-127')
            return False
        transport_prop_iface.Set(
                'org.bluez.MediaTransport1',
                'Volume',
                dbus.UInt16(vol))
    else:
        return False
    return True