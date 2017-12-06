import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.image import AsyncImage, Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.carousel import Carousel
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.logger import Logger
from shutil import copy

from yr.libyr import Yr
from bluesound.bluesound_control import Bluesound
from bluesound.bluesound_subscription_objects import title1, title2, title3, coverImage, streamState
from buttons import Source, EddaButtons


cover_image_path = "images/cover_image.png"


class IconButton(ButtonBehavior, AsyncImage):
    pass


class CoverArt(Image):
    pass


class EddaRoot(Carousel):
    def __init__(self, bluesound, **kwargs):
        super(EddaRoot, self).__init__(**kwargs)
        self.screen_dict = {Source.INFO.value: InfoScreen(), Source.PLAY.value: PlayScreen(bluesound)}
        for key, screen in self.screen_dict.items():
            self.add_widget(screen)

        self.buttons = EddaButtons(self, self.load_screen)

    def load_screen(self, screen_key):
        try:
            screen = self.screen_dict[screen_key.value]
        except KeyError:
            Logger.warning("Screen not implemented: {}".format(screen_key))
        else:
            if self.current_slide is not screen:
                Logger.info("Activate screen: {}".format(screen_key))
                self.load_slide(screen)


class PlayScreen(Widget):
    _artist = StringProperty("Stream music from another device")
    _album = StringProperty("")
    _title = StringProperty("")
    _stream_status_icon = StringProperty("icons/play.png")

    _album_art = StringProperty()
    coverart = ObjectProperty()

    def __init__(self, bluesound, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.bluesound = bluesound
        self.updateStreamStatus("pause")
        title1.setCallback(self.setTitle)
        title2.setCallback(self.setArtist)
        title3.setCallback(self.setAlbum)
        coverImage.setCallback(self.setAlbumArt)
        streamState.setCallback(self.updateStreamStatus)
        copy("images/kivy.jpg", cover_image_path)
        self._album_art = cover_image_path

    def setArtist(self, artist):
        self._artist = artist

    def setAlbum(self, album):
        self._album = album

    def setTitle(self, title):
        self._title = title

    def setAlbumArt(self, album_art):
        def changeCover(request, result):
            self.coverart.reload()

        UrlRequest(url=album_art, file_path=cover_image_path, on_success=changeCover)

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
        config = EddaApp.get_running_app().config
        yr_location = config.getdefault("Weather", "yr_location", "Norge/Oslo//Oslo/Oslo")
        self.update_weather_location(yr_location)

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
        config = self.get_running_app().config
        bluesound_ip = config.getdefault("Bluesound", "ip_address", "192.168.0.1")
        Logger.info("Connecting to Bluesound receiver with IP: {}".format(bluesound_ip))
        self.bluesound = Bluesound(bluesound_ip, 1.0, set([title1, title2, title3, coverImage, streamState]))
        self.bluesound.start()
        return EddaRoot(self.bluesound)

    def on_stop(self):
        self.bluesound.stop()

    def build_config(self, config):
        config.setdefaults('Bluesound', {'ip_address': "192.168.0.1"})
        config.setdefaults('Weather', {'yr_location': 'Norge/Oslo/Oslo/Oslo'})


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'resizable', 0)
    Window.size = (800, 480)
    EddaApp().run()
