# -------------------------------------------------------------------------------------------------------------------------- #
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
from math import *

# importação local
import var_globals
from carro import Car
from Garagem import Garagem

# -------------------------------------------------------------------------------------------------------------------------- #
# configurações globais
window = None
win_w, win_h = 1280, 720
tex_floor = None
quadric = None

# -------------------------------------------------------------------------------------------------------------------------- #
# Postes
post_height = 12.0

post_positions = [
    (15.0, 15.0, GL_LIGHT1),
    (-15.0, 15.0, GL_LIGHT2),
    (15.0, -15.0, GL_LIGHT3),
    (-15.0, -15.0, GL_LIGHT4),
]

posts_on = True

# -------------------------------------------------------------------------------------------------------------------------- #
# Carro
my_car = Car()

# -------------------------------------------------------------------------------------------------------------------------- #
# Sol
sun_angle = 170.0     
sun_distance = 100.0   
sun_color = (1.0, 0.95, 0.8, 1.0)

# -------------------------------------------------------------------------------------------------------------------------- #
# garagem
garagem = Garagem()

# -------------------------------------------------------------------------------------------------------------------------- #
# Texturas
TILE_PATH = "img/mosaico.jpg"

# -------------------------------------------------------------------------------------------------------------------------- #

def load_texture(path, repeat=True):
    """
    Carrega uma textura a partir de um ficheiro e retorna o ID da textura OpenGL.
    """

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


def init_gl(win_w, win_h):
    """
    Configurações iniciais do OpenGL.
    """


    global tex_floor
    glViewport(0, 0, win_w, win_h)
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    

    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.85, 0.85, 0.95, 1.0))
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 64.0)


    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_TEXTURE_2D)
    
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    glClearColor(0.75, 0.75, 1.0, 1.0)

    tex_floor = load_texture(TILE_PATH, repeat=True)

def set_projection(w, h):
    aspect = max(1.0, float(w)/float(max(h,1)))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, aspect, 0.05, 100.0)
    glMatrixMode(GL_MODELVIEW)

def set_material_light_post():
    """
    Configura os materiais para o poste de luz.
    """
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.1, 0.1, 0.1, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [0.4, 0.4, 0.4, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

def set_material_light_bulb(color=(1.0, 1.0, 0.8, 1.0)):
    """
    Configura os materiais para a lâmpada do poste de luz.
    """
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.0, 0.0, 0.0, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  color)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 80.0)


def draw_post(x=0.0, z=0.0, height=12.0, radius=.2, lamp_color=(1.0, 1.0, 0.8, 1.0), lid=GL_LIGHT1):
    """
    Desenha um poste com uma lâmpada no topo.
    """
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10.0)

    # cilindro do poste
    glPushMatrix()
    set_material_light_post()
    glTranslatef(x, 0.0, z)
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluCylinder(quadric, radius, radius, height, 16, 16)
    gluDeleteQuadric(quadric)
    glPopMatrix()

    # esfera da lampada
    lamp_height = height - 0.2
    glPushMatrix()
    set_material_light_bulb(lamp_color)
    glTranslatef(x - 0.3, lamp_height, z)
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, 0.6, 16, 16)
    gluDeleteQuadric(quadric)
    glPopMatrix()
    
    # cilindro do poste
    glPushMatrix()
    set_material_light_post()
    glTranslatef(x, 0.0, z)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(radius, height, 16, 16)
    glPopMatrix()

    #fazer as luzes
    global posts_on
    if posts_on:
        glPushMatrix()
        glEnable(lid) # ativo as luzes
        #defino elas
        LIGHT_CUTOFF   =  80.0     # meio larguinho
        LIGHT_EXPONENT = 1
        glLightfv(lid, GL_AMBIENT,  (0.08, 0.08, 0.09, 1.0))
        glLightfv(lid, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0)) # alterado apra cor difuisa 100% vermelha
        glLightfv(lid, GL_SPECULAR, (1.00, 1.00, 1.00, 1.0))
        glLightfv(lid, GL_POSITION, (x - 0.3, height, z, 1.0))
        glLightfv(lid, GL_SPOT_DIRECTION, (0.0, -1.0, 0.0))
        glLightf(lid, GL_SPOT_EXPONENT, LIGHT_EXPONENT)
        glLightf(lid, GL_SPOT_CUTOFF,   LIGHT_CUTOFF)
        glPopMatrix()
        print("ligada")
    else:
        print("desligada")
        glDisable(lid)
    

def draw_sun(angle_deg, distance=100.0, radius=3.0, color=(1.0,0.95,0.8,1.0)):
    """
    Desenha o sol na cena com base no ângulo, distância, raio e cor especificados.
    """

    ang = radians(angle_deg)
    sx = distance * cos(ang)
    sy = distance * sin(ang)
    sz = 0.0

    glPushMatrix()
    glTranslatef(sx, sy, sz)

    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [color[0], color[1], color[2], color[3]])
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, 32, 32)
    gluDeleteQuadric(quadric)
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0,0.0,0.0,1.0])
    glPopMatrix()

def update_sun():
    """
    Atualiza a posição e propriedades da luz do sol com base no ângulo, distância e cor atuais.
    """
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

    glPushAttrib(GL_ALL_ATTRIB_BITS)

    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    # ATIVAR color material APENAS PARA O CHÃO
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glColor3f(1.0, 1.0, 1.0)

    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glTexCoord2f(0, 0); glVertex3f(-S, 0,  S)
    glTexCoord2f(T, 0); glVertex3f( S, 0,  S)
    glTexCoord2f(T, T); glVertex3f( S, 0, -S)
    glTexCoord2f(0, T); glVertex3f(-S, 0, -S)
    glEnd()

    glPopAttrib()   # <- VOLTA TUDO AO NORMAL (materiais incluídos!)


def rotate_camera(angle):
    """
    Rotaciona a câmera em torno do ponto de olhar no plano XZ.
    """

    # vetor da câmera para o ponto de olhar
    dx = var_globals.eye_x - var_globals.leye_x
    dz = var_globals.eye_z - var_globals.leye_z
    radius = sqrt(dx**2 + dz**2)

    # ângulo atual
    theta = atan2(dz, dx)
    theta += angle  # rotaciona

    # nova posição da câmera
    var_globals.eye_x = var_globals.leye_x + radius * cos(theta)
    var_globals.eye_z = var_globals.leye_z + radius * sin(theta)

def move_camera_along_view(distance_delta):
    """
    Move a câmera ao longo da linha de visão para frente ou para trás.
    """
    # vetor da câmera para o ponto de olhar
    dx = var_globals.eye_x - var_globals.leye_x
    dz = var_globals.eye_z - var_globals.leye_z
    radius = sqrt(dx**2 + dz**2) + distance_delta  # aplica delta

    # angulo atual
    theta = atan2(dz, dx)

    # nova posição da câmera
    var_globals.eye_x = var_globals.leye_x + radius * cos(theta)
    var_globals.eye_z = var_globals.leye_z + radius * sin(theta)

def display():

    global sun_angle, sun_color, sun_distance

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(var_globals.eye_x, var_globals.eye_y, var_globals.eye_z,
              var_globals.leye_x, var_globals.leye_y, var_globals.leye_z,
              0.0, 1.0, 0.0) 

    # update sol
    update_sun()

    # update poste
    #update_post()
    
    # chao
    glEnable(GL_TEXTURE_2D)
    draw_floor()
    glDisable(GL_TEXTURE_2D)

    # sol
    draw_sun(sun_angle, distance=sun_distance, radius=3.0, color=sun_color)
    sun_angle += 0.1
    if sun_angle >= 360.0:
        sun_angle -= 360.0
    
    # postes de luz
    draw_post(x=15, z=15, height=post_height, lid=GL_LIGHT1)
    draw_post(x=-15, z=15, height=post_height, lid=GL_LIGHT2)
    draw_post(x=15, z=-15, height=post_height, lid=GL_LIGHT3)
    draw_post(x=-15, z=-15, height=post_height, lid=GL_LIGHT4)

    # garagem
    garagem.draw_garagem(0,0,0)
    # carro
    my_car.update_car()
    my_car.draw_car()
    

def glfw_resize(window, w, h):
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

keys_down = set()

def glfw_keyboard_callback(window, key, scancode, action, mods):
    
    global keys_down
    if action == glfw.PRESS:
        keys_down.add(key)
    elif action == glfw.RELEASE:
        keys_down.discard(key)
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

def keys_handler():
    global keys_down
    global garagem, my_car

    if glfw.KEY_UP in keys_down:
        my_car.drive("forward")
    if glfw.KEY_DOWN in keys_down:
        my_car.drive("backward")
    if glfw.KEY_LEFT in keys_down:
        my_car.drive("left")
    if glfw.KEY_RIGHT in keys_down:
        my_car.drive("right")
     
    step = 0.2
    step_angle = 0.1

    # se a camara estiver dentro do carro, não pode usar estas
    # keys
    if not my_car.car_camera:
        # movimentação da câmera ao redor de um ponto (centro)
        # esquerda/direita
        if glfw.KEY_A in keys_down:
            rotate_camera(step_angle)
        elif glfw.KEY_D in keys_down:
            rotate_camera(-step_angle)
        # cima/baixo
        elif glfw.KEY_W in keys_down:
            var_globals.eye_y += step
        elif glfw.KEY_S in keys_down:
            var_globals.eye_y -= step
        # aproximar/afastar
        elif glfw.KEY_P in keys_down:   
            move_camera_along_view(-5)
        elif glfw.KEY_O in keys_down:   
            move_camera_along_view(+5)
        # rotaçao da camara
        elif glfw.KEY_I in keys_down:
            var_globals.leye_y += 2
        elif glfw.KEY_K in keys_down:
            var_globals.leye_y -= 2
        elif glfw.KEY_J in keys_down:
            vetorX = var_globals.leye_x - var_globals.eye_x
            vetorZ = var_globals.leye_z - var_globals.eye_z
            length = sqrt(vetorX**2 + vetorZ**2)
            perpX = -vetorZ / length
            perpZ =  vetorX / length
            var_globals.leye_x += -perpX
            var_globals.leye_z += -perpZ
        elif glfw.KEY_L in keys_down:
            vetorX = var_globals.leye_x - var_globals.eye_x
            vetorZ = var_globals.leye_z - var_globals.eye_z
            length = sqrt(vetorX**2 + vetorZ**2)
            perpX = -vetorZ / length
            perpZ =  vetorX / length
            var_globals.leye_x += perpX 
            var_globals.leye_z += perpZ
    
    # funciona sempre
    if glfw.KEY_M in keys_down:
        garagem.last_time_garage = glfw.get_time()    #pega o tempo que começou o
        garagem.Abrir = not garagem.Abrir
    elif glfw.KEY_H in keys_down:
        my_car.toggle_door("right")
    elif glfw.KEY_G in keys_down:
        my_car.toggle_door("left")
    elif glfw.KEY_U in keys_down:
        my_car.change_car_camera_mode()
    elif glfw.KEY_R in keys_down:    # postes de luz
        global posts_on
        posts_on = not posts_on

def main():
    global window 

    if not glfw.init(): sys.exit("Falha ao inicializar GLFW")

    window = glfw.create_window(win_w, win_h, "Projeto CG Grupo 22", None, None)
    glfw.make_context_current(window)

    glfw.set_key_callback(window, glfw_keyboard_callback)
    init_gl(win_w, win_h)
    set_projection(win_w, win_h)

    while not glfw.window_should_close(window):
        keys_handler()
        display()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()



if __name__ == "__main__":
    main()
