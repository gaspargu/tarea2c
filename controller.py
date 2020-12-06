"""
Contralor de la aplicación.
"""

from model import Snake
import glfw
import sys
from typing import Union

class Controller(object):
    model: Union['Snake', None]

    def __init__(self):
        self.fill_polygon = True
        self.toggle = {}

    def set_toggle(self, tp, key):
        self.toggle[key] = tp

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_SPACE:
            self.fill_polygon = not self.fill_polygon

        elif key == glfw.KEY_F:
            self.toggle['face'].toggle()

        elif key == glfw.KEY_A:
            self.toggle['axis'].toggle()

        elif key == glfw.KEY_ESCAPE:
            sys.exit()

        else:
            print('Unknown key')
