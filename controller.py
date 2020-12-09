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
        self.vista_superior = False
        self.vista_diagonal = True
        self.primera_persona = False

    def set_snake(self, m):
        self.model = m

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_SPACE:
            self.fill_polygon = not self.fill_polygon

        if self.primera_persona:
            if key == glfw.KEY_LEFT and action == glfw.PRESS and self.model.dir[0][0] == 'left':
                self.model.move_down()
            if key == glfw.KEY_LEFT and action == glfw.PRESS and self.model.dir[0][0] == 'down':
                self.model.move_right()
            if key == glfw.KEY_LEFT and action == glfw.PRESS and self.model.dir[0][0] == 'up':
                self.model.move_left()
            if key == glfw.KEY_LEFT and action == glfw.PRESS and self.model.dir[0][0] == 'right':
                self.model.move_up()
            if key == glfw.KEY_RIGHT and action == glfw.PRESS and self.model.dir[0][0] == 'left':
                self.model.move_up()
            if key == glfw.KEY_RIGHT and action == glfw.PRESS and self.model.dir[0][0] == 'down':
                self.model.move_left()
            if key == glfw.KEY_RIGHT and action == glfw.PRESS and self.model.dir[0][0] == 'up':
                self.model.move_right()
            if key == glfw.KEY_RIGHT and action == glfw.PRESS and self.model.dir[0][0] == 'right':
                self.model.move_down()

        else:
            if key == glfw.KEY_LEFT and action == glfw.PRESS:
                self.model.move_left()
            if key == glfw.KEY_RIGHT and action == glfw.PRESS:
                self.model.move_right()
        
        if key == glfw.KEY_X and action == glfw.PRESS:
            # print('Move left')
            self.model.crece()            

        if key == glfw.KEY_UP and action == glfw.PRESS:
            # print('Move left')
            self.model.move_up()
            

        if key == glfw.KEY_DOWN and action == glfw.PRESS:
            # print('Move left')
            self.model.move_down()

        if key == glfw.KEY_E:
            self.vista_superior = True
            self.vista_diagonal = False
            self.primera_persona = False

        if key == glfw.KEY_T:
            self.vista_superior = False
            self.vista_diagonal = True
            self.primera_persona = False

        if key == glfw.KEY_R:
            self.vista_superior = False
            self.vista_diagonal = False
            self.primera_persona = True

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        else:
            print('Unknown key')
