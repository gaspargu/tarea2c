"""
Hacemos los modelos
"""

import scene_graph2 as sg
import basic_shapes as bs
import transformations2 as tr
import easy_shaders as es

from OpenGL.GL import *

d = 1

class Axis(object):

    def __init__(self):
        self.model = es.toGPUShape(bs.createAxis(1))
        self.show = True

    def toggle(self):
        self.show = not self.show

    def draw(self, pipeline, projection, view):
        if not self.show:
            return
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'model'), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(self.model, GL_LINES)


class Tpose(object):

    def __init__(self, texture_head):
        gpu_body = es.toGPUShape(bs.createColorCube(0, 1, 0))
        gpu_leg = es.toGPUShape(bs.createColorCube(0, 0, 1))
        gpu_skin = es.toGPUShape(bs.createColorCube(1, 1, 0))
        gpu_head = es.toGPUShape(bs.createTextureCube(texture_head), GL_REPEAT, GL_LINEAR)

        # Creamos el nucleo
        core = sg.SceneGraphNode('core')
        core.transform = tr.scale(0.32, 0.5, 0.6)
        core.childs += [gpu_body]

        # Piernas
        leg = sg.SceneGraphNode('leg')
        leg.transform = tr.scale(0.14, 0.14, 0.5)
        leg.childs += [gpu_leg]

        leg_left = sg.SceneGraphNode('leg_left')
        leg_left.transform = tr.translate(0, -0.17, -0.5)
        leg_left.childs += [leg]

        leg_right = sg.SceneGraphNode('leg_right')
        leg_right.transform = tr.translate(0, 0.17, -0.5)
        leg_right.childs += [leg]

        # Brazos
        arm = sg.SceneGraphNode('arm')
        arm.transform = tr.scale(0.13, 0.5, 0.13)
        arm.childs += [gpu_skin]

        arm_left = sg.SceneGraphNode('arm_left')
        arm_left.transform = tr.translate(0, -0.4, 0.23)
        arm_left.childs += [arm]

        arm_right = sg.SceneGraphNode('arm_right')
        arm_right.transform = tr.translate(0, 0.4, 0.23)
        arm_right.childs += [arm]

        # Cuello
        neck = sg.SceneGraphNode('neck')
        neck.transform = tr.matmul([tr.scale(0.12, 0.12, 0.2), tr.translate(0, 0, 1.6)])
        neck.childs += [gpu_skin]

        # Cabeza
        head = sg.SceneGraphNode('head')
        head.transform = tr.matmul([tr.scale(0.35, 0.35, 0.35), tr.translate(-0.08, 0, 1.75)])
        head.childs += [gpu_skin]

        body = sg.SceneGraphNode('body')
        body.childs += [arm_left, arm_right, leg_left, leg_right, core, neck, head]

        face = sg.SceneGraphNode('face')
        face.transform = tr.matmul([tr.scale(0.3, 0.3, 0.3), tr.translate(0, 0, 2)])
        face.childs += [gpu_head]

        body_tr = sg.SceneGraphNode('bodyTR')
        body_tr.childs += [body, face]

        self.model = body_tr
        self.show_face = True

    def toggle(self):
        self.show_face = not self.show_face

    def draw(self, pipeline_color, pipeline_texture, projection, view):
        # Dibujamos el mono de color con el pipeline_color
        glUseProgram(pipeline_color.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline_color.shaderProgram, 'projection'), 1, GL_TRUE,
                           projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline_color.shaderProgram, 'view'), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'body'), pipeline_color)

        # Dibujamos la cara (texturas)
        if self.show_face:
            glUseProgram(pipeline_texture.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline_texture.shaderProgram, 'projection'), 1, GL_TRUE,
                               projection)
            glUniformMatrix4fv(glGetUniformLocation(pipeline_texture.shaderProgram, 'view'), 1, GL_TRUE, view)
            sg.drawSceneGraphNode(sg.findNode(self.model, 'face'), pipeline_texture)

class Mapa(object):

    def __init__(self, texture_map):
        gpu_map = es.toGPUShape(bs.createTextureQuad(texture_map), GL_REPEAT, GL_NEAREST)

        # Creamos el mapa con sus dimensiones
        map = sg.SceneGraphNode('map')
        map.transform = tr.scale(1, 1, 0.3)
        map.childs += [gpu_map]

        #colocamos el mapa donde debe ir
        mapa = sg.SceneGraphNode('mapa')
        mapa.transform = tr.translate(0, 0, 0)
        mapa.childs += [map]

        self.model = mapa
    
    def draw(self, pipeline, projection, view):
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE,
                           projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(self.model, pipeline)

class Snake(object):
    def __init__(self, tamaño):
        self.tamaño = tamaño

        #centra la cabeza de la serpiente al comienzo
        if self.tamaño%2 == 0:
            self.pos = [[d/self.tamaño,d/self.tamaño],[d*3/self.tamaño,d/self.tamaño],[d*5/tamaño,d/self.tamaño],[d*7/tamaño,d/self.tamaño]]
            #self.pos = [[1/self.tamaño,1/self.tamaño],[3/self.tamaño,1/self.tamaño],[5/tamaño,1/self.tamaño]]
        else:
            self.pos = [[0,0],[d*2/self.tamaño,0],[d*4/self.tamaño,0],[d*6/self.tamaño,0]]
            #self.pos = [[0,0],[2/self.tamaño,0],[4/self.tamaño,0]]
        #self.dir = [['left','left'],['left','left'],['left','left']]
        self.dir = [['left','left'],['left','left'],['left','left'],['left','left']]

        self.die = False
        self.comio = False
        self.comio_cola = False
        self.comiendo = False

        # Figuras básicas
        #gpu_trozo = es.toGPUShape(bs.createColorQuad(0, 0.3, 0))  # verde
        gpu_trozo = es.toGPUShape(bs.createColorCube(1, 0, 0))
        gpu_trozo_cabeza =  es.toGPUShape(bs.createColorCube(0, 0, 1))

        

        trozo = sg.SceneGraphNode('trozo')
        trozo.transform = tr.uniformScale(d*2/self.tamaño)
        trozo.childs += [gpu_trozo]

        trozo_cabeza = sg.SceneGraphNode('trozo')
        trozo_cabeza.transform = tr.uniformScale(d*2/self.tamaño)
        trozo_cabeza.childs += [gpu_trozo_cabeza]
        
        cuerpo = sg.SceneGraphNode('cuerpo')
        cuerpo.childs += [trozo]

        cuerpo2 = sg.SceneGraphNode('cuerpo2')
        cuerpo2.childs += [trozo]

        cola = sg.SceneGraphNode('cola')
        cola.childs += [trozo]

        cabeza = sg.SceneGraphNode('cabeza')
        cabeza.childs += [trozo_cabeza]

        self.serpiente =[cabeza,cuerpo,cuerpo2,cola]
        #self.serpiente =[cabeza,cuerpo,cola]
        
        self.tiempo = 0



    def draw(self, pipeline, projection, view):
        for i in range(len(self.serpiente)):
            glUseProgram(pipeline.shaderProgram)
            self.serpiente[i].transform = tr.translate(self.pos[i][0], self.pos[i][1], 0)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE,
                           projection)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
            sg.drawSceneGraphNode(self.serpiente[i], pipeline)


    def update(self):
        for i in range(len(self.dir)):
            new_dir = self.dir[i][0]
            if new_dir == 'left':
                self.pos[i][0] -= d*2/self.tamaño
                
            elif new_dir == 'right':
                self.pos[i][0] += d*2/self.tamaño
            
            elif new_dir == 'up':
                self.pos[i][1] += d*2/self.tamaño 
            
            elif new_dir == 'down':
                self.pos[i][1] -= d*2/self.tamaño
               

    def move_left(self):
        old_dir = self.dir[0][1]
        if old_dir != 'right':
            self.dir[0][0] = 'left'  
            
    def move_right(self):
        old_dir = self.dir[0][1]
        if old_dir != 'left':
            self.dir[0][0] = 'right'            

    def move_up(self):
        old_dir = self.dir[0][1]
        if old_dir != 'down':
            self.dir[0][0] = 'up' 

    def move_down(self):
        old_dir = self.dir[0][1]
        if old_dir != 'up':
            self.dir[0][0] = 'down'

    def come_manzana(self, manzana: 'Manzana'):
        #if math.trunc(100*manzana.pos_x) == math.trunc(100*self.pos[0][0]) and math.trunc(100*manzana.pos_y) == math.trunc(100*self.pos[0][1]):
        if abs(manzana.pos_x - self.pos[0][0]) < d*0.5/self.tamaño and abs(manzana.pos_y - self.pos[0][1])< d*0.5/self.tamaño:
            self.comio = True

    def come_cola(self):
        for i in range(1,len(self.pos)):
            if abs(self.pos[0][0] - self.pos[i][0]) < d/self.tamaño and abs(self.pos[0][1] - self.pos[i][1]) < d/self.tamaño:
                self.comio_cola = True


    def crece(self):
        tamaño_snake = len(self.dir)
        direccion_cola = self.dir[-1][1]
        #self.pos += [self.pos[-1]]
        if direccion_cola == 'left':
            self.pos += [[self.pos[-1][0], self.pos[-1][1]]]
        elif direccion_cola == 'right':
            self.pos +=[[self.pos[-1][0], self.pos[-1][1]]]
        elif direccion_cola == 'up':
            self.pos += [[self.pos[-1][0], self.pos[-1][1]]]
        else:
            self.pos += [[self.pos[-1][0], self.pos[-1][1]]]
        self.dir += [['stop','stop']]
  

        gpu_trozo = es.toGPUShape(bs.createTextureQuad('cuerpo.png'), GL_REPEAT, GL_NEAREST)

        trozo = sg.SceneGraphNode('trozo')
        trozo.transform = tr.uniformScale(d*2/self.tamaño)
        trozo.childs += [gpu_trozo]

        aum = sg.SceneGraphNode(str(tamaño_snake))
        aum.childs += [trozo]

        self.serpiente += [aum]