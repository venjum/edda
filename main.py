from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from bluesound.bluesound_control import Bluesound
from bluesound.bluesound_subscription_objects import title1, title2, title3, coverImage, streamState
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior


class IconButton(ButtonBehavior, AsyncImage):
    pass


class PlayScreen(Widget):
    _artist = StringProperty("kivy.org")
    _album = StringProperty("kivy.org")
    _title = StringProperty("kivy.org")
    _album_art = StringProperty("images/kivy.jpg")
    _stream_status_icon = StringProperty("images/play.png")

    def __init__(self):
        super(PlayScreen, self).__init__()
        self.updateStreamStatus("pause")
        self.bluesound = Bluesound("192.168.1.87", 1.0, set([title1, title2, title3, coverImage, streamState]))

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
        if state == "pause":
            self._stream_status_icon = "images/play.png"
        else:
            self._stream_status_icon = "images/pause.png"

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


class EddaApp(App):
    def build(self):
        self.app = PlayScreen()
        title1.setCallback(self.app.setTitle)
        title2.setCallback(self.app.setArtist)
        title3.setCallback(self.app.setAlbum)
        coverImage.setCallback(self.app.setAlbumArt)
        streamState.setCallback(self.app.updateStreamStatus)

        self.app.bluesound.start()
        return self.app

    def on_stop(self):
        self.app.bluesound.stop()


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'resizable', 0)

    from kivy.core.window import Window
    Window.size = (800, 480)
    EddaApp().run()
