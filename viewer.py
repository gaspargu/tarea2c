"""
Visualizador.
"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys

import transformations2 as tr2
import easy_shaders as es
import lighting_shaders as ls

from model import Axis, Mapa, Snake, Kirby
from controller import Controller


if __name__ == '__main__':

    d = 1

    tamaño = 40
    width = (20*tamaño + 40)*d
    height = (20*tamaño + 40)*d

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 1000

    window = glfw.create_window(width, height, 'Snake 3D', None, None)

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
    lightShaderProgram = ls.SimpleGouraudShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creamos los objetos
    axis = Axis()
    snake = Snake(tamaño)
    kirby = Kirby(tamaño, 'img/carrot.obj', 'img/kirby.png')
    mapa = Mapa(tamaño, 'img/pasto.png', 'img/esquina.png')

    controller.set_snake(snake)

    #controller.set_toggle(tpose, 'face')
    #controller.set_toggle(axis, 'axis')

    # Creamos la camara y la proyección
    projection = tr2.ortho(-1.5, 1.5, -1.5, 1.5, 0.1, 600)
    #viewPos = np.array([-30, -30, 60])
    viewPos = np.array([0, 0, 60])
    view = tr2.lookAt(
        viewPos,  # Donde está parada la cámara
        np.array([0, 0, 0]),  # Donde estoy mirando
        np.array([0, 1, 0])  # Cual es vector UP
    )

    contador = 0

    while not glfw.window_should_close(window):

        t = glfw.get_time()

        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if controller.fill_polygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        velocidad = 0.1 #Velocidad snake: Mayor es más lento

        tamaño_snake = len(snake.dir)

        if t>velocidad:
            if snake.comiendo:
                contador += 1
            else:
                contador = 0
            
            t = glfw.set_time(0)

            snake.update()

            if contador == tamaño_snake-1:
                snake.crece()
                snake.comiendo = False
                contador = 0
            
            for i in range(tamaño_snake-2,-1,-1):
                snake.dir[i][1] = snake.dir[i][0]
                snake.dir[i+1][0] = snake.dir[i][0]
            
            
            snake.come_manzana(kirby)
            snake.come_cola()
            if snake.comio:
                print("ñomi ñomi")
                kirby.fue_comida(snake)
                snake.comiendo = True
                snake.comio = False

        
        # Dibujamos
        #axis.draw(colorShaderProgram, projection, view)
        mapa.draw(textureShaderProgram, projection, view)
        snake.draw(colorShaderProgram, projection, view)
        #glUseProgram(lightShaderProgram.shaderProgram)
        kirby.draw(lightShaderProgram, projection, view, viewPos)

        #tpose.draw(colorShaderProgram, textureShaderProgram, projection, view)


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
