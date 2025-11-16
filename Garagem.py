import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
from math import *
from math import sqrt,cos,sin,atan2


class Garagem:
    ANGLE_GARAGE = 0
    Abrir = False
    last_time_garage = 0

    def draw_porta_garagem(self,x,y,z,comprimento = 7.5, altura = 5,faixas = 10):
        glPushMatrix()
        glNormal3f(0.0, 1.0, 0.0) 
        glTranslatef(x,y,z) #posição dada
        #glTranslatef(0.0, altura/2, 0.0)  # posiciona acima do chão

        #começa self.Abrir e fechar
        #--------------------------------------//------------------------------------------
        #mecanismo de self.Abrir e fechar a porta
        if self.Abrir and self.ANGLE_GARAGE <90:
            # gira em torno do eixo superior
            t = glfw.get_time()
            self.ANGLE_GARAGE += 30.0 * max(0.0, t - self.last_time_garage)
            self.last_time_garage = t
        elif not self.Abrir and self.ANGLE_GARAGE > 0:
            t = glfw.get_time()
            self.ANGLE_GARAGE -= 30.0 * max(0.0, t - self.last_time_garage)
            self.last_time_garage = t 
        if self.ANGLE_GARAGE > 90: #teste de erros caso a garagem vá muito para cima ou para baixo
            self.ANGLE_GARAGE = 90
        elif self.ANGLE_GARAGE < 0:
            self.ANGLE_GARAGE = 0
        glTranslatef(0.0, altura, 0.0) # faz com que as tranformações ocorram no eixo superior
        glRotatef(self.ANGLE_GARAGE, 1, 0, 0)  
        glTranslatef(0.0, -altura, 0.0)
        altura_per_faixa = altura / faixas
        y_atual = 0
        for i in range(faixas):
            tom = 0.4 + 0.05 * (i % 2)
            glColor3f(tom, tom, tom)
            glBegin(GL_QUADS)
            glVertex2f(-comprimento/2,y_atual)
            glVertex2f(comprimento/2,y_atual)
            glVertex2f(comprimento/2,y_atual + altura_per_faixa)
            glVertex2f(-comprimento/2,y_atual + altura_per_faixa)
            glEnd()
            y_atual += altura_per_faixa

        glColor3f(0.7, 0.8, 0.7)#usa uma cor escura para para o portão
        glPopMatrix()
    
    def draw_wall_garagem(self,x,y,z,angle_rotation = 0, qntVigas=10,comprimento=10,altura=7, largura =0.2, comprimento_viga = 0.1, cor_viga =(0.7,0.7,0.7)):
        glPushMatrix()
        glNormal3f(0.0, 1.0, 0.0) 
        glTranslatef(x,y,z) 
        #desenha a parede
        glColor3f(0.2,0.2,0.2) # quase preeto
        glRotatef(angle_rotation,0,1,0)
        glBegin(GL_QUADS)
        glVertex2f(-comprimento/2,0)
        glVertex2f(comprimento/2,0)
        glVertex2f(comprimento/2,altura)
        glVertex2f(-comprimento/2,altura)
        glEnd()
        glPopMatrix()

        glPushMatrix()
        glColor3f(*cor_viga)
        #glTranslatef(0,0,largura) #ficar ao lado da parede
        comprimento_relacao = comprimento_viga/altura
        dist_vigas = comprimento / (qntVigas) #começar e acabar com uma viga
        largura_relacao = largura/altura 
        glTranslatef(x,y+ altura/2,z)
        glRotatef(angle_rotation,0,1,0)
        glTranslatef(-dist_vigas * (qntVigas//2),0,comprimento_viga/2)
        glScalef(largura_relacao,1,comprimento_relacao)
        for i in range(qntVigas):
            glPushMatrix()  
            glTranslatef(i * dist_vigas / largura_relacao, 0,0)
            glNormal3f(0.0, 1.0, 0.0) 
            glRotatef(90,0,1,0)
            glutSolidCube(altura)
            glPopMatrix()

        glPopMatrix()


    def draw_teto_garagem(self,x,y,z,comprimento = 7.5, largura = 10):
        glPushMatrix()
        glTranslatef(x,y,z)
        glRotatef(90,1,0,0)
        self.draw_wall_garagem(0,0,0,comprimento = comprimento,altura=largura,comprimento_viga=-0.1)
        glPopMatrix()

    def draw_porta_garagem(self,x,y,z,comprimento = 7.5, altura = 5,faixas = 10):
        glPushMatrix()
        glNormal3f(0.0, 1.0, 0.0) 
        glTranslatef(x,y,z) #posição dada
        #glTranslatef(0.0, altura/2, 0.0)  # posiciona acima do chão

        #começa self.Abrir e fechar
        #--------------------------------------//------------------------------------------
        #mecanismo de self.Abrir e fechar a porta
        if self.Abrir and self.ANGLE_GARAGE <90:
            # gira em torno do eixo superior
            t = glfw.get_time()
            self.ANGLE_GARAGE += 30.0 * max(0.0, t - self.last_time_garage)
            self.last_time_garage = t
        elif not self.Abrir and self.ANGLE_GARAGE > 0:
            t = glfw.get_time()
            self.ANGLE_GARAGE -= 30.0 * max(0.0, t - self.last_time_garage)
            self.last_time_garage = t 
        if self.ANGLE_GARAGE > 90: #teste de erros caso a garagem vá muito para cima ou para baixo
            self.ANGLE_GARAGE = 90
        elif self.ANGLE_GARAGE < 0:
            self.ANGLE_GARAGE = 0
        glTranslatef(0.0, altura, 0.0) # faz com que as tranformações ocorram no eixo superior
        glRotatef(self.ANGLE_GARAGE, 1, 0, 0)  
        glTranslatef(0.0, -altura, 0.0)
        altura_per_faixa = altura / faixas
        y_atual = 0
        for i in range(faixas):
            tom = 0.4 + 0.05 * (i % 2)
            glColor3f(tom, tom, tom)
            glBegin(GL_QUADS)
            glVertex2f(-comprimento/2,y_atual)
            glVertex2f(comprimento/2,y_atual)
            glVertex2f(comprimento/2,y_atual + altura_per_faixa)
            glVertex2f(-comprimento/2,y_atual + altura_per_faixa)
            glEnd()
            y_atual += altura_per_faixa

        glColor3f(0.7, 0.8, 0.7)#usa uma cor escura para para o portão
        glPopMatrix()
        
    def draw_garagem(self,x,y,z):
        comprimento_porta = 7.5
        altura_porta = 5
        comprimento_parede = 15
        altura_parede = 7
        self.draw_porta_garagem(x,y,z,comprimento=7.5,altura=5,faixas=10)

        self.draw_wall_garagem(x+comprimento_porta/2,y,
                        z+comprimento_parede/2, 
                        angle_rotation=90,
                        qntVigas=11,
                        comprimento_viga=0.10,
                        comprimento=comprimento_parede)
        
        self.draw_wall_garagem(x+-comprimento_porta/2,y,z+comprimento_parede/2,
                        angle_rotation=90,qntVigas=11, comprimento_viga=-0.1
                        ,comprimento=comprimento_parede)

        self.draw_wall_garagem(x,y+altura_porta,z,angle_rotation= 0,comprimento=7.5,altura = 2,comprimento_viga=-0.1)
        
        self.draw_wall_garagem(x,y,z+comprimento_parede,angle_rotation= 0,comprimento=7.5,comprimento_viga=0.1)
        
        self.draw_teto_garagem(x,y+altura_parede,z,largura=comprimento_parede)