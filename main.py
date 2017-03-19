import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.carousel import Carousel
from kivy.core.window import Window

from bluesound.bluesound_control import Bluesound
from bluesound.bluesound_subscription_objects import title1, title2, title3, coverImage, streamState
from yr.libyr import Yr


class IconButton(ButtonBehavior, AsyncImage):
    pass


class EddaRoot(Carousel):
    def __init__(self, bluesound, **kwargs):
        super(EddaRoot, self).__init__(**kwargs)
        self.infoscreen = InfoScreen()
        self.playscreen = PlayScreen(bluesound)
        self.add_widget(self.infoscreen)
        self.add_widget(self.playscreen)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.load_infoscreen()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] is '1':
            self.load_infoscreen()
        elif keycode[1] is '2':
            self.load_playscreen()
        return True

    def load_infoscreen(self):
        if self.current_slide is not self.infoscreen:
            self.load_slide(self.infoscreen)

    def load_playscreen(self):
        if self.current_slide is not self.playscreen:
            self.load_slide(self.playscreen)


class PlayScreen(Widget):
    _artist = StringProperty("Stream music from another device")
    _album = StringProperty("")
    _title = StringProperty("")
    _album_art = StringProperty("images/kivy.jpg")
    _stream_status_icon = StringProperty("icons/play.png")

    def __init__(self, bluesound, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.bluesound = bluesound
        self.updateStreamStatus("pause")
        title1.setCallback(self.setTitle)
        title2.setCallback(self.setArtist)
        title3.setCallback(self.setAlbum)
        coverImage.setCallback(self.setAlbumArt)
        streamState.setCallback(self.updateStreamStatus)

    def setArtist(self, artist):
        self._artist = artist

    def setAlbum(self, album):
        self._album = album

    def setTitle(self, title):
        self._title = title

    def setAlbumArt(self, album_art):
        self._album_art = album_art

    def updateStreamStatus(self, state):
        self._state = state
        if state == "pause" or state == "stop":
            self._stream_status_icon = "icons/play.png"
        else:
            self._stream_status_icon = "icons/pause.png"

# Buttons
    def playPauseSong(self):
        if self._state == "pause":
            self.bluesound.play()
        else:
            self.bluesound.pause()
        self.bluesound.readStatusNow()

    def previousSong(self):
        self.bluesound.back()

    def nextSong(self):
        self.bluesound.skip()


class Weather(BoxLayout):
    icon = StringProperty("icons/yr/02d.png")
    location = StringProperty("Oslo")
    temperature = StringProperty('30')
    precipitation = StringProperty('2')
    wind_speed = StringProperty('4')

    def __init__(self, **kwargs):
        super(Weather, self).__init__(**kwargs)
        self.update_weather_location('Norge/Oslo/Oslo/Løren')

    def update_weather_location(self, location):
        self.location_full_name = location
        self.location = self.location_full_name.split('/')[-1]
        self.update_weather()

    def update_weather(self):
        weather = Yr(location_name=self.location_full_name)
        now = weather.now()
        self.icon = "icons/yr/{}.png".format(now['symbol']['@var'])
        self.temperature = now['temperature']['@value']
        self.precipitation = now['precipitation']['@value']
        self.wind_speed = now['windSpeed']['@mps']


class TimeScreen(BoxLayout):
    """docstring for TimeScreen"""
    clock = StringProperty("")
    weekday = StringProperty("")
    date = StringProperty("")

    def updated_time(self):
        time_now = time.localtime()
        self.clock = time.strftime("%H:%M", time_now)
        self.weekday = time.strftime("%A", time_now)
        self.date = time.strftime("%d. %B", time_now)


class InfoScreen(BoxLayout):
    timescreen = ObjectProperty()
    currentweather = ObjectProperty()

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)
        Clock.schedule_interval(self.update_weather, 15*60)

    def update_time(self, dt):
        self.timescreen.updated_time()

    def update_weather(self, dt):
        self.currentweather.update_weather()


class EddaApp(App):
    def build(self):
        self.bluesound = Bluesound("192.168.1.87", 1.0, set([title1, title2, title3, coverImage, streamState]))
        self.bluesound.start()
        return EddaRoot(self.bluesound)

    def on_stop(self):
        self.bluesound.stop()


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'resizable', 0)
    Window.size = (800, 480)
    EddaApp().run()
