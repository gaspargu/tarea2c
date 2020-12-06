"""
Visualizador.
"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys

import transformations2 as tr2
import easy_shaders as es

from model import Tpose, Axis, Mapa, Snake
from controller import Controller

if __name__ == '__main__':

    d = 1

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 1000

    window = glfw.create_window(width, height, 'TPOSE EPIC', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Creamos el controlador
    controller = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    # Creating shader programs for textures and for colores
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creamos los objetos
    axis = Axis()
    tpose = Tpose('img/face.png')
    snake = Snake(30)
    mapa = Mapa('img/pasto.png')

    controller.set_toggle(tpose, 'face')
    controller.set_toggle(axis, 'axis')

    # Creamos la camara y la proyección
    projection = tr2.ortho(-1, 1, -1, 1, 0.1, 100)
    view = tr2.lookAt(
        np.array([30, 30, 20]),  # Donde está parada la cámara
        np.array([0, 0, 0]),  # Donde estoy mirando
        np.array([0, 0, 1])  # Cual es vector UP
    )

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if controller.fill_polygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Dibujamos
        axis.draw(colorShaderProgram, projection, view)
        mapa.draw(textureShaderProgram, projection, view)
        snake.draw(colorShaderProgram, projection, view)
        #tpose.draw(colorShaderProgram, textureShaderProgram, projection, view)


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
