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
from car import Car
from garage import Garage

# -------------------------------------------------------------------------------------------------------------------------- #
# configurações globais
window = None
win_w, win_h = 1280, 720
tex_floor = None
quadric = None
keys_down = set()

# -------------------------------------------------------------------------------------------------------------------------- #
# Camera
step = 0.2
step_angle = 0.1

# -------------------------------------------------------------------------------------------------------------------------- #

# Postes
post_height = 12.0
posts_on = True

# -------------------------------------------------------------------------------------------------------------------------- #
# Carro
my_car = Car()

# -------------------------------------------------------------------------------------------------------------------------- #
# Sol
sun_angle = 90.0     
sun_distance = 100.0   
sun_color = (1.0, 0.95, 0.8, 1.0)

# -------------------------------------------------------------------------------------------------------------------------- #
# garagem
garagem = Garage()

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
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluCylinder(quadric, radius, radius, height, 16, 16)
    gluDeleteQuadric(quadric)
    glPopMatrix()

    #fazer as luzes
    global posts_on
    if posts_on:
        glPushMatrix()
        glEnable(lid) # ativo as luzes
        #defino elas
        LIGHT_CUTOFF   =  85.0
        LIGHT_EXPONENT = 0.0
        glLightfv(lid, GL_AMBIENT,  (0.08, 0.08, 0.09, 1.0))
        glLightfv(lid, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0)) 
        glLightfv(lid, GL_SPECULAR, (1.00, 1.00, 1.00, 1.0))
        glLightfv(lid, GL_POSITION, (x - 0.3, height, z, 1.0))
        glLightfv(lid, GL_SPOT_DIRECTION, (0.0, -1.0, 0.0))
        glLightf(lid, GL_SPOT_EXPONENT, LIGHT_EXPONENT)
        glLightf(lid, GL_SPOT_CUTOFF,   LIGHT_CUTOFF)
        glPopMatrix()
    else:
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
    
    # fazer reset à emissão
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
    sun_position = [sun_x, sun_y, sun_z, 0]
    sun_diffuse = [sun_color[0] * intensity, sun_color[1] * intensity, sun_color[2] * intensity , 1.0]
    sun_specular = [sun_color[0] * intensity, sun_color[1] * intensity, sun_color[2] * intensity, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, sun_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_specular)

    # ajustar de acordo com a altura Y do sol
    if sun_y > 0:
        glEnable(GL_LIGHT0)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)
    else:
        glDisable(GL_LIGHT0)
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 1.0) 

def draw_floor():
    """
    Desenha o chão texturizado.
    """

    # distância
    S = 100.0
    # tamanho dos tiles
    T = 10.0

    step = 10.0

    glDisable(GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.04, 0.04, 0.04, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [0.2, 0.2, 0.2, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10.0)

    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glNormal3f(0.0, 1.0, 0.0)

    # transfomar em int para o range
    start_int = int(-S)
    end_int = int(S)
    step_int = int(step)
    
    glBegin(GL_QUADS)
    for x in range(start_int, end_int, step_int):
        for z in range(start_int, end_int, step_int):
            # vértices do quad
            x0 = float(x)
            z0 = float(z)
            x1 = float(x + step_int)
            z1 = float(z + step_int)
           # coordenadas de textura
            s0 = (x0 + S) / (2 * S) * T
            t0 = (z0 + S) / (2 * S) * T
            s1 = (x1 + S) / (2 * S) * T
            t1 = (z1 + S) / (2 * S) * T

            glTexCoord2f(s0, t0); glVertex3f(x0, 0, z1) 
            glTexCoord2f(s1, t0); glVertex3f(x1, 0, z1) 
            glTexCoord2f(s1, t1); glVertex3f(x1, 0, z0) 
            glTexCoord2f(s0, t1); glVertex3f(x0, 0, z0) 
    glEnd()


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
    
    # chao
    glEnable(GL_TEXTURE_2D)
    draw_floor()
    glDisable(GL_TEXTURE_2D)

    # sol
    draw_sun(sun_angle, distance=sun_distance, radius=3.0, color=sun_color)
    sun_angle += 0.10
    sun_angle = sun_angle % 360.0
    
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

def glfw_keyboard_callback(window, key, scancode, action, mods):
    
    global keys_down, my_car, garagem
    
    if action == glfw.PRESS:
        keys_down.add(key)

        if key == glfw.KEY_R:
            global posts_on
            posts_on = not posts_on
        
        if key == glfw.KEY_U:
            my_car.change_car_camera_mode()

        if key == glfw.KEY_M:
            garagem.last_time_garage = glfw.get_time()
            garagem.Abrir = not garagem.Abrir
            
        if key == glfw.KEY_H:
            my_car.toggle_door("right")
            
        if key == glfw.KEY_G:
            my_car.toggle_door("left")

    elif action == glfw.RELEASE:
        keys_down.discard(key)
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

def keys_handler():
    global keys_down
    global garagem, my_car, step, step_angle
    global step

    # Carro
    if glfw.KEY_UP in keys_down:
        my_car.drive("forward")
    if glfw.KEY_DOWN in keys_down:
        my_car.drive("backward")
    if glfw.KEY_LEFT in keys_down:
        my_car.drive("left")
    if glfw.KEY_RIGHT in keys_down:
        my_car.drive("right")

    # Camera (se a camara nao estiver no interior do carro)
    if not my_car.car_camera:
        # zoom in/out
        if glfw.KEY_P in keys_down:
            move_camera_along_view(-step)
        if glfw.KEY_O in keys_down:
            move_camera_along_view(step)
        
        # rotate à volta de um ponto
        if glfw.KEY_A in keys_down:
            rotate_camera(step_angle)
        if glfw.KEY_D in keys_down:
            rotate_camera(-step_angle)
        
        # Mover camara up/down
        if glfw.KEY_W in keys_down:
            var_globals.eye_y += step
        if glfw.KEY_S in keys_down:
            var_globals.eye_y -= step
        
        # rotacao central à camara
        if glfw.KEY_I in keys_down:
            var_globals.leye_y += step
        if glfw.KEY_K in keys_down:
            var_globals.leye_y -= step
            
        if glfw.KEY_J in keys_down:
            vetorX = var_globals.leye_x - var_globals.eye_x
            vetorZ = var_globals.leye_z - var_globals.eye_z
            length = sqrt(vetorX**2 + vetorZ**2)
            if length > 0:
                perpX = -vetorZ / length
                perpZ = vetorX / length
                var_globals.leye_x += -perpX * step
                var_globals.leye_z += -perpZ * step

        if glfw.KEY_L in keys_down:
            vetorX = var_globals.leye_x - var_globals.eye_x
            vetorZ = var_globals.leye_z - var_globals.eye_z
            length = sqrt(vetorX**2 + vetorZ**2)
            if length > 0:
                perpX = -vetorZ / length
                perpZ = vetorX / length
                var_globals.leye_x += perpX * step
                var_globals.leye_z += perpZ * step 

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
