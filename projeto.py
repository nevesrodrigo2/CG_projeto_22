import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
from math import *

import var_globals
from carro import Car

win_w, win_h = 900, 600
tex_floor = None

my_car = Car()

# -------------------------------------------------------------------------------------------------------------------------- #
# Sol
sun_angle = 45.0     
sun_distance = 100.0   
sun_color = (1.0, 0.95, 0.8, 1.0)
# -------------------------------------------------------------------------------------------------------------------------- #

# garagem
ANGLE_GARAGE = 0
SIZE = 5

START_TIME = 0

GRUNGE_PATH = "Texturelabs_Grunge_197M.jpg"

ABRIR = False

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

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glShadeModel(GL_FLAT)
    glClearColor(0.75, 0.75, 1.0, 1.0)

    tex_floor = load_texture(GRUNGE_PATH, repeat=True)

def draw_sun(angle_deg, distance=100.0, radius=3.0, color=(1.0,0.95,0.8,1.0)):
    ang = radians(angle_deg)
    sx = distance * cos(ang)
    sy = distance * sin(ang)
    sz = 0.0

    glPushMatrix()
    glTranslatef(sx, sy, sz)

    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [color[0], color[1], color[2], color[3]])
    glColor3f(*color[:3])
    glutSolidSphere(radius, 32, 32)
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0,0.0,0.0,1.0])
    
    glPopMatrix()

def update_sun():
    global sun_angle, sun_distance, sun_color
    
    ang = radians(sun_angle)
    sun_x = sun_distance * cos(ang)
    sun_y = sun_distance * sin(ang)
    sun_z = 0.0

    sun_position = [sun_x, sun_y, sun_z, 1.0]
    sun_diffuse = [sun_color[0], sun_color[1], sun_color[2], 1.0]
    sun_specular = [sun_color[0], sun_color[1], sun_color[2], 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, sun_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_specular)

def draw_floor():
    S = 100.0
    T = 10.0
    glBindTexture(GL_TEXTURE_2D, tex_floor)
    glColor3f(1, 1, 1)
    glNormal3f(0, 1, 0)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-S, 0.0,  S)
    glTexCoord2f(T,   0.0); glVertex3f( S, 0.0,  S)
    glTexCoord2f(T,    T ); glVertex3f( S, 0.0, -S)
    glTexCoord2f(0.0,  T ); glVertex3f(-S, 0.0, -S)
    glEnd()

def draw_wall_garagem(x,y,z,qntVigas=10,comprimento=10,altura=7, largura =2, comprimento_viga = 0.5, cor_viga =3):
    glPushMatrix()
    glNormal3f(0.0, 1.0, 0.0) 
    glTranslate(x,y,z)
    glColor3f(0.3,0.3,0.3)
    glBegin(GL_QUADS)
    glPopMatrix()

def draw_porta_garagem(x,y,z,comprimento = 7.5, altura = 5,faixas = 10):
    global ABRIR,ANGLE_GARAGE, last_t
    glPushMatrix()
    glNormal3f(0.0, 1.0, 0.0) 
    glTranslate(x,y,z)

    if ABRIR and ANGLE_GARAGE <90:
        t = glfw.get_time()
        ANGLE_GARAGE += 30.0 * max(0.0, t - last_t)
        last_t = t
    elif not ABRIR and ANGLE_GARAGE > 0:
        t = glfw.get_time()
        ANGLE_GARAGE -= 30.0 * max(0.0, t - last_t)
        last_t = t 
    ANGLE_GARAGE = max(0.0, min(ANGLE_GARAGE, 90))

    glTranslatef(0.0, altura, 0.0)
    glRotatef(ANGLE_GARAGE, 1, 0, 0)
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

    glColor3f(0.7, 0.8, 0.7)
    glPopMatrix()


def display():
    global sun_angle, sun_color, sun_distance

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(var_globals.eye_x, var_globals.eye_y, var_globals.eye_z,
              var_globals.leye_x, var_globals.leye_y, var_globals.leye_z,
              0.0, 1.0, 0.0) 

    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 10.0, 5.0, 1.0))

    update_sun()
    draw_sun(sun_angle, distance=sun_distance, radius=3.0, color=sun_color)
    sun_angle += 0.1
    if sun_angle >= 360.0:
        sun_angle -= 360.0

    draw_floor()
    draw_porta_garagem(0,0,0)
    my_car.update_car()
    my_car.draw_car()

    glutSwapBuffers()

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), 0.1, 1000.0)


from math import sqrt,cos,sin,atan2
def keyboard(key, x, y):
    global ABRIR
    global my_car
    
    step = 0.2
    step_angle = 0.1
    if key == b'a': 
        r = sqrt(var_globals.eye_x ** 2 + var_globals.eye_z ** 2)
        tetha = atan2(var_globals.eye_z, var_globals.eye_x) + step_angle
        var_globals.eye_x = r * cos(tetha)
        var_globals.eye_z = r * sin(tetha)
    elif key == b'd':
        r = sqrt(var_globals.eye_x ** 2 + var_globals.eye_z ** 2)
        tetha = atan2(var_globals.eye_z, var_globals.eye_x) - step_angle
        var_globals.eye_x = r * cos(tetha)
        var_globals.eye_z = r * sin(tetha)
    elif key == b'w':
        var_globals.eye_y += step
    elif key == b's':
        var_globals.eye_y -= step
    elif key == b'm':
        global last_t
        last_t = glfw.get_time()
        ABRIR = not ABRIR
    elif key == b'p':
        var_globals.eye_z -= 3
    elif key == b'o':
        var_globals.eye_z += 3
    elif key == b'h':
        my_car.toggle_door("right")
    elif key == b'g':
        my_car.toggle_door("left")
    elif key == b'i':
        my_car.drive("forward")
    elif key == b'k':
        my_car.drive("backward")
    elif key == b'j':
        my_car.drive("left")
    elif key == b'l':
        my_car.drive("right")
    elif key == b'u':
        my_car.change_car_camera_mode()
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
    glutCreateWindow(b"Pipeline Fixo (Flat) : Cubo e Chao texturados")
    setup()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()
