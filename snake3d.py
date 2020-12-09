"""
Visualizador.
"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys
import random


import basic_shapes as bs
import transformations2 as tr2
import easy_shaders as es
import lighting_shaders as ls

from model import Axis, Mapa, Snake, Kirby, GameOver
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
    
    game_over = GameOver()
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
    frames = True

    while not glfw.window_should_close(window):

        t = glfw.get_time()
        theta = glfw.get_time()

        # Using GLFW to check for input events
        glfw.poll_events()

        

        if controller.primera_persona and not(snake.die):
            # Creamos la camara y la proyección
            
            v = 0.2
            w = 0
            if snake.dir[0][0] == 'left':
                v = 0
                w = -0.2
            elif snake.dir[0][0] == 'right':
                v = 0
                w = 0.2
            elif snake.dir[0][0] == 'up':
                v = 0.2
                w = 0
            else:
                v = -0.2
                w = 0
            projection = tr2.perspective(20, 2/1, 0.1, 100)
            #viewPos = np.array([-30, -30, 60])
            viewPos = np.array([snake.pos[0][0]-w*0.7, snake.pos[0][1]-v*0.7, 0.06])
            

            view = tr2.lookAt(
                viewPos,  # Donde está parada la cámara
                np.array([snake.pos[0][0]+w*1.5, snake.pos[0][1]+v*1.5, 0]),  # Donde estoy mirando
                np.array([0, 0, 1])  # Cual es vector UP
            )
        elif controller.vista_superior:
            # Creamos la camara y la proyección
            projection = tr2.ortho(-1.5, 1.5, -1.5, 1.5, 0.1, 600)
            #viewPos = np.array([-30, -30, 60])
            viewPos = np.array([0, 0, 60])
            view = tr2.lookAt(
                viewPos,  # Donde está parada la cámara
                np.array([0, 0, 0]),  # Donde estoy mirando
                np.array([0, 1, 0])  # Cual es vector UP
            )
        elif snake.die:
            # Creamos la camara y la proyección
            projection = tr2.perspective(30, 1, 0.1, 100)
            #viewPos = np.array([-30, -30, 60])
            viewPos = np.array([0, 0, 6])
            view = tr2.lookAt(
                viewPos,  # Donde está parada la cámara
                np.array([0, 0, 0]),  # Donde estoy mirando
                np.array([0, 1, 0])  # Cual es vector UP
            )

        else:
            # Creamos la camara y la proyección
            #projection = tr2.ortho(-1.5, 1.5, -1.5, 1.5, 0.1, 600)
            projection = tr2.perspective(30, 1, 0.1, 100)
            #viewPos = np.array([-30, -30, 60])
            viewPos = np.array([-3, -3, 4])
            view = tr2.lookAt(
                viewPos,  # Donde está parada la cámara
                np.array([0, 0, 0]),  # Donde estoy mirando
                np.array([0, 0, 1])  # Cual es vector UP
            )

        # Filling or not the shapes depending on the controller state
        if controller.fill_polygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        



        velocidad = 0.1 #Velocidad snake: Mayor es más lento

        tamaño_snake = len(snake.dir)

        if t>snake.velocidad:
            if snake.comiendo:
                contador += 1
            else:
                contador = 0
            
            t = glfw.set_time(0)
            frames = not(frames)

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
            snake.choca_esquina()
            if snake.comio:
                print("ñomi ñomi")
                if random.random() < 0.3:
                    kirby.atenuacion = 0.01
                    kirby.ka = 1
                    kirby.fue_comida(snake)
                    snake.comiendo = True
                    snake.comio = False
                    snake.velocidad = 0.03
                else:
                    kirby.atenuacion = 0.1
                    kirby.ka = 0.2
                    kirby.fue_comida(snake)
                    snake.comiendo = True
                    snake.comio = False
                    snake.velocidad = 0.1
                
                

        
        # Dibujamos
        #axis.draw(colorShaderProgram, projection, view)
        mapa.draw(textureShaderProgram, projection, view)
        snake.draw(colorShaderProgram, projection, view)
        #glUseProgram(lightShaderProgram.shaderProgram)
        kirby.draw(lightShaderProgram, projection, view, viewPos)

        

        if snake.die and frames:

            game_over.draw1(textureShaderProgram, projection, view)

        if snake.die and not(frames):

            game_over.draw2(textureShaderProgram, projection, view)




            
        

        #tpose.draw(colorShaderProgram, textureShaderProgram, projection, view)


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
