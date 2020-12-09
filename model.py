"""
Hacemos los modelos
"""

import scene_graph2 as sg
import basic_shapes as bs
import transformations2 as tr
import easy_shaders as es
import random
import numpy as np



from OpenGL.GL import *

d = 1

def readFaceVertex(faceDescription):

    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]

    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex



def readOBJ(filename, color):

    vertices = []
    normals = []
    textCoords= []
    faces = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split(' ')
            
            if aux[0] == 'v':
                vertices += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                textCoords += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'f':
                N = len(aux)                
                faces += [[readFaceVertex(faceVertex) for faceVertex in aux[1:4]]]
                for i in range(3, N-1):
                    faces += [[readFaceVertex(faceVertex) for faceVertex in [aux[i], aux[i+1], aux[1]]]]

        vertexData = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0,3):
                vertex = vertices[face[i][0]-1]
                normal = normals[face[i][2]-1]

                vertexData += [
                    vertex[0], vertex[1], vertex[2],
                    color[0], color[1], color[2],
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3        

        return bs.Shape(vertexData, indices)
           


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

class Mapa(object):

    def __init__(self, tamaño, texture_map, texture_esquina):
        self.tamaño = tamaño

        gpu_map = es.toGPUShape(bs.createTextureQuad(texture_map), GL_REPEAT, GL_NEAREST)
        gpu_esquina_quad = es.toGPUShape(bs.createTextureQuad(texture_esquina), GL_REPEAT, GL_NEAREST)  # negro
        
        esquina_vertical = sg.SceneGraphNode('esquinaVertical')
        esquina_vertical.transform = tr.scale(d*4/self.tamaño,2.1,1)
        esquina_vertical.childs += [gpu_esquina_quad]

        esquina_horizontal = sg.SceneGraphNode('esquinaHorizontal')
        esquina_horizontal.transform = tr.scale(2,d*4/self.tamaño,1)
        esquina_horizontal.childs += [gpu_esquina_quad]

        esquina_der = sg.SceneGraphNode('esquinaDerecha')
        esquina_der.transform = tr.translate(1,0,0)
        esquina_der.childs += [esquina_vertical]

        esquina_izq = sg.SceneGraphNode('esquinaIzquierda')
        esquina_izq.transform = tr.translate(-1,0,0)
        esquina_izq.childs += [esquina_vertical]

        esquina_sup = sg.SceneGraphNode('esquinaIzquierda')
        esquina_sup.transform = tr.translate(0,1,0)
        esquina_sup.childs += [esquina_horizontal]

        esquina_inf = sg.SceneGraphNode('esquinaIzquierda')
        esquina_inf.transform = tr.translate(0,-1,0)
        esquina_inf.childs += [esquina_horizontal]

        # Creamos el mapa con sus dimensiones
        map = sg.SceneGraphNode('map')
        map.transform = tr.uniformScale(1.9)
        map.childs += [gpu_map]

        #colocamos el mapa donde debe ir
        mapa = sg.SceneGraphNode('mapa')
        mapa.transform = tr.translate(0, 0, 0)
        mapa.childs += [map, esquina_der, esquina_izq, esquina_sup, esquina_inf]

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
        self.velocidad = 0.1

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
        gpu_trozo = es.toGPUShape(bs.createColorCube(0, 0.5, 0.5))
        gpu_trozo_cabeza =  es.toGPUShape(bs.createColorCube(0, 0.5, 0.5))

        

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

    def come_manzana(self, kirby: 'Kirby'):
        #if math.trunc(100*manzana.pos_x) == math.trunc(100*self.pos[0][0]) and math.trunc(100*manzana.pos_y) == math.trunc(100*self.pos[0][1]):
        if abs(kirby.pos_x - self.pos[0][0]) < d*0.5/self.tamaño and abs(kirby.pos_y - self.pos[0][1])< d*0.5/self.tamaño:
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
  

        gpu_trozo = es.toGPUShape(bs.createColorCube(0, 0.5, 0.5))

        trozo = sg.SceneGraphNode('trozo')
        trozo.transform = tr.uniformScale(d*2/self.tamaño)
        trozo.childs += [gpu_trozo]

        aum = sg.SceneGraphNode(str(tamaño_snake))
        aum.childs += [trozo]

        self.serpiente += [aum]

class Kirby(object):
    def __init__(self, tamaño, obj, obj_texture):
        self.tamaño = tamaño
        self.atenuacion = 0.1
        self.ka = 0.2

        gpu_kirby = es.toGPUShape(readOBJ(obj, (1,0.7,0.8)))
        
        prekirby = sg.SceneGraphNode('prekirby')
        prekirby.transform = tr.matmul([
                tr.uniformScale(0.15),
                tr.rotationX(np.pi/2)])
        prekirby.childs += [gpu_kirby]

        self.pos_x = -1 + d*3/self.tamaño + d*2/self.tamaño*random.randint(0,self.tamaño-3)
        self.pos_y = -1 + d*3/self.tamaño + d*2/self.tamaño*random.randint(0,self.tamaño-3)

        kirby = sg.SceneGraphNode('kirby')
        #kirby.childs += [prekirby]
        kirby.childs += [prekirby]

        self.model = kirby
        


    def draw(self, pipeline, projection, view, viewPos):
        self.model.transform = tr.translate(self.pos_x,self.pos_y,0)

        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, self.ka, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -3, 0, 3)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), self.atenuacion)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(0.01))
        sg.drawSceneGraphNode(self.model, pipeline)

    def malpuesta(self, snake: 'Snake'):
        for i in range(len(snake.pos)):
            if abs(self.pos_x - self.pos[i][0]) < d*0.5/self.tamaño and abs(self.pos[i][0] - self.pos[i][0]) < d*0.5/self.tamaño:
                self.comio_cola = True

    def fue_comida(self, snake: 'Snake'):
        self.pos_x = -1 + d*3/self.tamaño + d*2/self.tamaño*random.randint(0,self.tamaño-3)
        self.pos_y = -1 + d*3/self.tamaño + d*2/self.tamaño*random.randint(0,self.tamaño-3)

