import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
from math import *

import var_globals
from carro import Car
from Garagem import Garagem

win_w, win_h = 1280, 720
tex_floor = None
quadric = None
# -------------------------------------------------------------------------------------------------------------------------- #
# Postes
post_height = 12.0
post_length = 2.0
post_color = (0.5, 0.5, 0.5, 1.0)

post_positions = [
    (15.0, 15.0, GL_LIGHT1),
    (-15.0, 15.0, GL_LIGHT2),
    (15.0, -15.0, GL_LIGHT3),
    (-15.0, -15.0, GL_LIGHT4),
]

posts_on = True
#------------------------------------------ #
# Carro
my_car = Car()
# -------------------------------------------------------------------------------------------------------------------------- #
# Sol
sun_angle = 45.0     
sun_distance = 100.0   
sun_color = (1.0, 0.95, 0.8, 1.0)
# -------------------------------------------------------------------------------------------------------------------------- #
# garagem
garagem = Garagem()
# -------------------------------------------------------------------------------------------------------------------------- #
# Texturas
GRUNGE_PATH = "img/Texturelabs_Grunge_197M.jpg"
GRASS_PATH = "img/relva.png"
TILE_PATH = "img/mosaico.jpg"
# -------------------------------------------------------------------------------------------------------------------------- #

def load_texture(path, repeat=True):
    if not os.path.isfile(path):
        print("Texture not found:", path); sys.exit(1)

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    data = img.tobytes("raw", "RGBA", 0, -1)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)

    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)

    return tex_id


def setup():
    global tex_floor
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    glClearColor(0.75, 0.75, 1.0, 1.0)

    tex_floor = load_texture(TILE_PATH, repeat=True)


def draw_sphere(centro = (0,0,0),color = (0.85, 0.65, 0.35), raio = 1):
    global quadric

    glPushMatrix()
    glTranslatef(*centro)
    glColor3f(*color)
    #glRotatef(90, 1, 0, 0)      # rodar 90° em X
    gluSphere(quadric, raio, 48, 32)
    glPopMatrix()

def draw_circle(raio, centro = (0,0,0)):
    global quadric

    glPushMatrix()
    glTranslatef(*centro)
    gluDisk(quadric,0.0,raio,50,1)
    glPopMatrix()
    
def draw_cylinder(centro = (0,0,0), color = (0.85, 0.65, 0.35), base = 1.0,top = 1.0,height = 3):
    global quadric
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(*centro)
    draw_circle(base)
    draw_circle(top,(0,0,+height))
    gluCylinder(quadric, base, top, height, 48, 32)
    glPopMatrix()

def draw_post(x=0.0, z=0.0, height=12.0, radius=.2, lamp_color=(1.0, 1.0, 0.8, 1.0), lid=GL_LIGHT1):
    # cilindro do poste
    glPushMatrix()
    set_material_light_post()
    glTranslatef(x, 0.0, z)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(radius, height, 16, 16)
    glPopMatrix()

    # esfera da lampada
    lamp_height = height - 0.2
    glPushMatrix()
    set_material_light_bulb(lamp_color)
    glTranslatef(x - 0.3, lamp_height, z)
    glutSolidSphere(0.6, 16, 16)
    glPopMatrix()

    glPushMatrix()
    glEnable(lid)
    glLightfv(lid, GL_POSITION, (x - 0.3, lamp_height, z, 1.0))
    glLightfv(lid, GL_DIFFUSE, lamp_color)
    glLightfv(lid, GL_SPECULAR, lamp_color)
    glLightfv(lid, GL_AMBIENT, [0.1*c for c in lamp_color])
    glLightf(lid, GL_CONSTANT_ATTENUATION, 0.5)
    glLightf(lid, GL_LINEAR_ATTENUATION, 0.01)
    glLightf(lid, GL_QUADRATIC_ATTENUATION, 0.001)
    glLightf(lid, GL_SPOT_CUTOFF, 90.0)  # omnidirectional
    glPopMatrix()
    
def update_post():
    global posts_on
    if posts_on:
        for _, _, lid in post_positions:
            glEnable(lid)
    else:
        for _, _, lid in post_positions:
            glDisable(lid)

def draw_sun(angle_deg, distance=100.0, radius=3.0, color=(1.0,0.95,0.8,1.0)):
    ang = radians(angle_deg)
    sx = distance * cos(ang)
    sy = distance * sin(ang)
    sz = 0.0

    glPushMatrix()
    glTranslatef(sx, sy, sz)

    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [color[0], color[1], color[2], color[3]])
    glutSolidSphere(radius, 32, 32)
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0,0.0,0.0,1.0])
    glPopMatrix()

def update_sun():
    global sun_angle, sun_distance, sun_color

    
    ang = radians(sun_angle)
    sun_x = sun_distance * cos(ang)
    sun_y = sun_distance * sin(ang)
    sun_z = 0.0

    intensity = 2
    sun_position = [sun_x, sun_y, sun_z, 1.0]  # posicao da luz
    sun_diffuse = [sun_color[0] * intensity, sun_color[1] * intensity, sun_color[2] * intensity , 1.0]
    sun_specular = [sun_color[0] * intensity, sun_color[1] * intensity, sun_color[2] * intensity, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, sun_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_specular)

    # ajustar de acordo com a altura Y do sol
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [0.0, -1.0, 0.0])
    if sun_y > 0:
        glEnable(GL_LIGHT0)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)
    else:
        glDisable(GL_LIGHT0)
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0) 

def draw_floor():
    S = 100.0
    T = 10.0

    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glTexCoord2f(0.0, 0.0); glVertex3f(-S, 0.0,  S)
    glTexCoord2f(T,   0.0); glVertex3f( S, 0.0,  S)
    glTexCoord2f(T,    T ); glVertex3f( S, 0.0, -S)
    glTexCoord2f(0.0,  T ); glVertex3f(-S, 0.0, -S)
    glEnd()

def set_material_light_post():
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.1, 0.1, 0.1, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [0.4, 0.4, 0.4, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

def set_material_light_bulb(color=(1.0, 1.0, 0.8, 1.0)):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.0, 0.0, 0.0, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  color)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 80.0)
    
def display():
    global sun_angle, sun_color, sun_distance

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(var_globals.eye_x, var_globals.eye_y, var_globals.eye_z,
              var_globals.leye_x, var_globals.leye_y, var_globals.leye_z,
              0.0, 1.0, 0.0) 

    update_sun()

    for x, z, lid in post_positions:
        glPushMatrix()
        glLoadIdentity()
        glLightfv(lid, GL_POSITION, (x - 0.3, post_height - 0.2, z, 1.0))
        glPopMatrix()

    update_post()
    
    # draw floor
    glEnable(GL_TEXTURE_2D)
    draw_floor()
    glDisable(GL_TEXTURE_2D)

    draw_sun(sun_angle, distance=sun_distance, radius=3.0, color=sun_color)
    sun_angle += 0.1
    if sun_angle >= 360.0:
        sun_angle -= 360.0
    
    draw_post(x=15, z=15, height=post_height, lid=GL_LIGHT1)
    draw_post(x=-15, z=15, height=post_height, lid=GL_LIGHT2)
    draw_post(x=15, z=-15, height=post_height, lid=GL_LIGHT3)
    draw_post(x=-15, z=-15, height=post_height, lid=GL_LIGHT4)

    garagem.draw_garagem(0,0,0)
    my_car.update_car()
    my_car.draw_car()
    
    glutSwapBuffers()

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), 0.1, 1000.0)

def specialKeyboard(key, x, y):
    if key == GLUT_KEY_UP:
        my_car.drive("forward")
    elif key == GLUT_KEY_DOWN:
        my_car.drive("backward")
    elif key == GLUT_KEY_LEFT:
        my_car.drive("left")
    elif key == GLUT_KEY_RIGHT:
        my_car.drive("right")

from math import sqrt,cos,sin,atan2
def keyboard(key, x, y):
    global garagem
    global my_car
    
    step = 0.2
    step_angle = 0.1

    # se a camara estiver dentro do carro, não pode usar estas
    # keys
    if not my_car.CameraDeCarro:
        if key == b'a':
            subx = var_globals.eye_x - var_globals.leye_x
            subz = var_globals.eye_z - var_globals.leye_z
            r = sqrt(subx ** 2 + subz ** 2)
            tetha = atan2(subz, subx) + step_angle
            var_globals.eye_x = var_globals.leye_x + r * cos(tetha)
            var_globals.eye_z = var_globals.leye_z + r * sin(tetha)
        elif key == b'd':
            subx = var_globals.eye_x - var_globals.leye_x
            subz = var_globals.eye_z - var_globals.leye_z
            r = sqrt(subx ** 2 + subz ** 2)
            tetha = atan2(subz, subx) - step_angle
            var_globals.eye_x = var_globals.leye_x + r * cos(tetha)
            var_globals.eye_z = var_globals.leye_z + r * sin(tetha)
        elif key == b'w':
            var_globals.eye_y += step
        elif key == b's':
            var_globals.eye_y -= step
        elif key == b'p':
            dist = sqrt((var_globals.eye_x - var_globals.leye_x) ** 2 + (var_globals.eye_z - var_globals.leye_z) ** 2) - 5
            tetha = atan2(var_globals.eye_z - var_globals.leye_z, var_globals.eye_x - var_globals.leye_x)
            var_globals.eye_x = var_globals.leye_x + dist * cos(tetha)
            var_globals.eye_z = var_globals.leye_z + dist * sin(tetha)
        elif key == b'o':
            dist = sqrt((var_globals.eye_x - var_globals.leye_x) ** 2 + (var_globals.eye_z - var_globals.leye_z) ** 2) + 5
            tetha = atan2(var_globals.eye_z - var_globals.leye_z, var_globals.eye_x - var_globals.leye_x)
            var_globals.eye_x = var_globals.leye_x + dist * cos(tetha)
            var_globals.eye_z = var_globals.leye_z + dist * sin(tetha)
        elif key == b'i':
            var_globals.leye_y += 2
        elif key ==b'k':
            var_globals.leye_y -= 2
        elif key ==b'j':
            vetorX = var_globals.leye_x - var_globals.eye_x
            vetorZ = var_globals.leye_z - var_globals.eye_z
            length = sqrt(vetorX**2 + vetorZ**2)
            perpX = -vetorZ / length
            perpZ =  vetorX / length
            var_globals.leye_x += -perpX
            var_globals.leye_z += -perpZ
        elif key ==b'l':
            vetorX = var_globals.leye_x - var_globals.eye_x
            vetorZ = var_globals.leye_z - var_globals.eye_z
            length = sqrt(vetorX**2 + vetorZ**2)
            perpX = -vetorZ / length
            perpZ =  vetorX / length
            var_globals.leye_x += perpX 
            var_globals.leye_z += perpZ
    
    # funciona sempre
    if key == b'm':
        garagem.last_time_garage = glfw.get_time()    #pega o tempo que começou o
        garagem.Abrir = not garagem.Abrir
    elif key == b'h':
        my_car.toggle_door("right")
    elif key == b'g':
        my_car.toggle_door("left")
    elif key == b'u':
        my_car.change_car_camera_mode()
    elif key == b'r':    # postes de luz
        global posts_on
        posts_on = not posts_on
    elif key in (b'\x1b', b'q'):
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)
    glutPostRedisplay()

def main():
    if not glfw.init(): sys.exit("Falha ao inicializar GLFW")
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"Projeto CG Grupo 22")
    setup()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeyboard)
    glutIdleFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()
