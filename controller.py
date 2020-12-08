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
        self.model = None

    def set_snake(self, m):
        self.model = m

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_SPACE:
            self.fill_polygon = not self.fill_polygon

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        # Controlador modifica al modelo
        elif key == glfw.KEY_LEFT and action == glfw.PRESS:
            # print('Move left')
            self.model.move_left()

        elif key == glfw.KEY_RIGHT and action == glfw.PRESS:
            # print('Move left')
            self.model.move_right()

        elif key == glfw.KEY_X and action == glfw.PRESS:
            # print('Move left')
            self.model.crece()            

        elif key == glfw.KEY_UP and action == glfw.PRESS:
            # print('Move left')
            self.model.move_up()
            

        elif key == glfw.KEY_DOWN and action == glfw.PRESS:
            # print('Move left')
            self.model.move_down()

        elif key == glfw.KEY_ESCAPE:
            sys.exit()

        else:
            print('Unknown key')
