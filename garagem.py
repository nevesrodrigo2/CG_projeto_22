import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
import math

win_w, win_h = 900, 600
tex_floor = None
quadric = None

ANGLE_GARAGE = 0
SIZE = 5



GRUNGE_PATH = "relva.png"

ABRIR = False
eye_x, eye_y, eye_z = 0.0, 5.0, 14.0
leye_x, leye_y, leye_z = 0.0, 5.0, 0
def load_texture(path, repeat=True):
    #asoscia-se a imagem à variavel, e se ela se repete
    if not os.path.isfile(path):
        print("Texture not found:", path); sys.exit(1)

    #converte a imagem para tipo RGBA
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    data = img.tobytes("raw", "RGBA", 0, -1)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # filtros  e  mipmaps (veremos esta parte mais tarde )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)

    # Criação de mipmaps com o GLU
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)

    #devolve o ID de cada textura carregada que será usado quando os objectos forem desenhados
    return tex_id

def setup():
    global tex_floor
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Luz simples <- componentes RGB iguais - luz branca (cinzenta) - Não altera cor dos objectos
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 10.0, 5.0, 1.0))  #Posição <- Alta e para tras da câmara
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))   # Luz difusa
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.5, 0.5, 0.5, 1.0))   # Luz ambiente

    # Vamos permitir que as texturas sejam ilumnadas por multiplicação com a luz
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glShadeModel(GL_FLAT)
    glClearColor(0.75, 0.75, 1.0, 1.0)

    
    # Carregar as texturas 
    
    tex_floor = load_texture(GRUNGE_PATH, repeat=True)    # grunge no floor Atenção ao repeat!!

def draw_floor():
    S = 100.0                 
    T = 10.0                  # Quantas vezes multiplicaremos a textura original no chão
    glBindTexture(GL_TEXTURE_2D, tex_floor)
    glColor3f(1, 1, 1)        # Não mexer na cor
    glNormal3f(0, 1, 0)

    glBegin(GL_QUADS)
    #2d texture, ou seja ele vai do ponto 0,0 0,t t,t 0,t e deve repetir isso para o resto dos pontos
    glTexCoord2f(0.0, 0.0); glVertex3f(-S, 0.0,  S)
    glTexCoord2f(T,   0.0); glVertex3f( S, 0.0,  S)
    glTexCoord2f(T,    T ); glVertex3f( S, 0.0, -S)
    glTexCoord2f(0.0,  T ); glVertex3f(-S, 0.0, -S)
    glEnd()

def draw_sphere(centro = (0,0,0),color = (0.85, 0.65, 0.35), raio = 1):
    glPushMatrix()
    glTranslatef(*centro)
    glColor3f(*color)
    #glRotatef(90, 1, 0, 0)      # rodar 90° em X
    gluSphere(quadric, raio, 48, 32)
    glPopMatrix()

def draw_circle(raio, centro = (0,0,0)):
    glPushMatrix()
    glTranslatef(*centro)
    gluDisk(quadric,0.0,raio,50,1)
    glPopMatrix()
    
def draw_cylinder(centro = (0,0,0), color = (0.85, 0.65, 0.35), base = 1.0,top = 1.0,height = 3):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(*centro)
    draw_circle(base)
    draw_circle(top,(0,0,+height))
    gluCylinder(quadric, base, top, height, 48, 32)
    glPopMatrix()

#def draw_poste_iluminacao(pos = (0,0,0),height = 5):
    

def draw_wall_garagem(x,y,z,angle_rotation = 0, qntVigas=10,comprimento=10,altura=7, largura =0.2, comprimento_viga = 0.1, cor_viga =(0.7,0.7,0.7)):
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

def draw_teto_garagem(x,y,z,comprimento = 7.5, largura = 10):
    glPushMatrix()
    glTranslatef(x,y,z)
    glRotatef(90,1,0,0)
    draw_wall_garagem(0,0,0,comprimento = comprimento,altura=largura,comprimento_viga=-0.1)
    glPopMatrix()

def draw_porta_garagem(x,y,z,comprimento = 7.5, altura = 5,faixas = 10):
    global ABRIR,ANGLE_GARAGE, last_time_garage
    glPushMatrix()
    glNormal3f(0.0, 1.0, 0.0) 
    glTranslatef(x,y,z) #posição dada
    #glTranslatef(0.0, altura/2, 0.0)  # posiciona acima do chão

    #começa abrir e fechar
    #--------------------------------------//------------------------------------------
    #mecanismo de abrir e fechar a porta
    if ABRIR and ANGLE_GARAGE <90:
        # gira em torno do eixo superior
        t = glfw.get_time()
        ANGLE_GARAGE += 30.0 * max(0.0, t - last_time_garage)
        last_time_garage = t
    elif not ABRIR and ANGLE_GARAGE > 0:
        t = glfw.get_time()
        ANGLE_GARAGE -= 30.0 * max(0.0, t - last_time_garage)
        last_time_garage = t 
    if ANGLE_GARAGE > 90: #teste de erros caso a garagem vá muito para cima ou para baixo
        ANGLE_GARAGE = 90
    elif ANGLE_GARAGE < 0:
        ANGLE_GARAGE = 0
    glTranslatef(0.0, altura, 0.0) # faz com que as tranformações ocorram no eixo superior
    glRotatef(ANGLE_GARAGE, 1, 0, 0)  
    glTranslatef(0.0, -altura, 0.0)
    #acabar o mecanismo de fechar a porta
    #------------------------------------------//----------------------------------------

    #Desenhar o retangulo da garagem
    #glScalef(0.03,1,1.3)
    #glutSolidCube(size)
    #defenir pontos
    #--------------------------------------//--------------------------------------------
    #parte da frente do portão
    #desenha a figura primeiro no centro
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

def draw_garagem(x,y,z):
    comprimento_porta = 7.5
    altura_porta = 5
    comprimento_parede = 10
    altura_parede = 7
    draw_porta_garagem(x,y,z,comprimento=7.5,altura=5,faixas=10)
    draw_wall_garagem(x+comprimento_porta/2,y,z+altura_porta, angle_rotation=90,qntVigas=11,comprimento_viga=0.10)
    draw_wall_garagem(x+-comprimento_porta/2,y,z+altura_porta, angle_rotation=90,qntVigas=11, comprimento_viga=-0.1)
    draw_wall_garagem(x,y+altura_porta,z,angle_rotation= 0,comprimento=7.5,altura = 2,comprimento_viga=-0.1)
    draw_wall_garagem(x,y,z+comprimento_parede,angle_rotation= 0,comprimento=7.5,comprimento_viga=0.1)
    draw_teto_garagem(x,y+altura_parede,z)

def display():
    global eye_x,eye_y,eye_z
    global leye_x,leye_y,leye_z
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eye_x, eye_y, eye_z,   # eye
              leye_x, leye_y, leye_z,   # center
              0.0, 1.0, 0.0)   # up

    # recolocar a posição da luz a cada frame
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 10.0, 5.0, 1.0))

    draw_floor()
    glDisable(GL_TEXTURE_2D)
    draw_garagem(0,0,0)
    glEnable(GL_TEXTURE_2D)
    glutSwapBuffers()

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), 0.1, 1000.0)


from math import sqrt,cos,sin,atan2
def keyboard(key, x, y):
    global eye_x, eye_y,eye_z
    global leye_x,leye_y,leye_z
    global ABRIR
    
    step = 0.2
    step_angle = 0.1
    cube_spet = 1
    if key == b'a': 
        r = sqrt(eye_x ** 2 + eye_z ** 2)
        tetha = atan2(eye_z, eye_x) + step_angle
        eye_x = r * cos(tetha)
        eye_z = r * sin(tetha)
    elif key == b'd':  # Rotate right
        r = sqrt(eye_x ** 2 + eye_z ** 2)
        tetha = atan2(eye_z, eye_x) - step_angle
        eye_x = r * cos(tetha)
        eye_z = r * sin(tetha)
    elif key == b'w':
        eye_y +=step
    elif key == b's':
        eye_y -= step
    elif key == b'l':
        global last_time_garage
        last_time_garage = glfw.get_time()    #pega o tempo que começou o sinal
        ABRIR = not ABRIR
    elif key == b'p':
        eye_z -= 3
    elif key == b'o':
        eye_z += 3
    elif key in (b'\x1b', b'q'):  # ESC or q
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)
    
    glutPostRedisplay()

def main():
    global quadric
    if not glfw.init(): sys.exit("Falha ao inicializar GLFW")
    glutInit(sys.argv)
    quadric = gluNewQuadric(); gluQuadricNormals(quadric, GLU_SMOOTH)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"Pipeline Fixo (Flat) : Cubo e Chao texturados")
    setup()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(display)
    glutMainLoop()
    if quadric: gluDeleteQuadric(quadric)

if __name__ == "__main__":
    main()
