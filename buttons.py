from kivy.core.window import Window
from kivy.logger import Logger

from enum import Enum, unique
import RPi.GPIO as GPIO
import time

MAX_TIME_BUTTON_HIGH_AND_LOW = 0.5


@unique
class Source(Enum):
    """ Source selection for Bluesound receiver.
    Enum value is also the BCM number where the button is connected

    ## Pinout
    https://pinout.xyz
    """
    INFO = 0        # Info screen is activated when all buttons is inactive (Button 0)
    PLAY = 18       # Button 1
    BUTTON_2 = 23   # Button 2
    BUTTON_3 = 24   # Button 3
    BUTTON_4 = 25   # Button 4
    BUTTON_5 = 12   # Button 5
    BUTTON_6 = 16   # Button 6
    BUTTON_7 = 20   # Button 7


def init_raspberry_gpio(callback):
    """ Init GPIO and interrupt on Raspberry pi
    https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
    """
    GPIO.setmode(GPIO.BCM)
    for button in Source:
        # Setup GPIO to input and with internal pull up
        GPIO.setup(button.value, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # add rising edge detection on a channel, ignoring further edges for 200ms for switch bounce handling
        GPIO.add_event_detect(button.value, GPIO.BOTH, callback=callback, bouncetime=600)
    Logger.info("GPIO initialization done")


class EddaButtons(object):
    """Class for handling all buttons on Edda radio
    """
    def __init__(self, root, callback_source_select):
        # super(EddaButtons, self).__init__()
        self._callback_source_select = callback_source_select
        self._root = root

        # Use keyboard to toggel modes too
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self._root)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._callback_source_select(Source.INFO)
        init_raspberry_gpio(self.gpio_callback)
        self.last_callback_s = 0

    def gpio_callback(self, channel):
        def wait_for_high():
            """ High takes longer time because of the internal pull up
            """
            for _ in range(5):
                if GPIO.input(channel) == GPIO.HIGH:
                    return True
                else:
                    time.sleep(0.01)
            return False

        try:
            source = Source(channel)
        except ValueError:
            Logger.error("channel {} not in Source enum".format(channel))
        else:
            channel_value = wait_for_high()
            Logger.info("Button interrupt from button: {}, button is {}".format(source, channel_value))
            now = time.time()
            if not channel_value:
                self._callback_source_select(source)
            else:
                if now - self.last_callback_s > MAX_TIME_BUTTON_HIGH_AND_LOW:
                    self._callback_source_select(Source.INFO)
            self.last_callback_s = now

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] is '1':
            self._callback_source_select(Source.INFO)
        elif keycode[1] is '2':
            self._callback_source_select(Source.PLAY)
        return True
