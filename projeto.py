import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
from math import *

win_w, win_h = 900, 600
tex_floor = None

# carro
car_speed = 0.0
car_direction = 0.0
car_x = 5
car_y = 1.0
car_z = 10.0
left_door_angle = 0.0
right_door_angle = 0.0
left_door_open = False
right_door_open = False
lift = 1
wheel_angle = 0.0
steering_wheel_angle = 0.0
steering_angle = 0.0  
MAX_STEERING = 30.0   
STEERING_SPEED = 5.0   

# garagem
ANGLE_GARAGE = 0
SIZE = 5

START_TIME = 0

GRUNGE_PATH = "Texturelabs_Grunge_197M.jpg"

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

def draw_wall_garagem(x,y,z,qntVigas=10,comprimento=10,altura=7, largura =2, comprimento_viga = 0.5, cor_viga =3):
    glPushMatrix()
    glNormal3f(0.0, 1.0, 0.0) 
    glTranslate(x,y,z)
    #desenha a parede
    glColor3f(0.3,0.3,0.3)
    glBegin(GL_QUADS)

    glPopMatrix()

def draw_wheel(pos = (0,0,0), radius = 0.7, width = 0.4, angle = 0.0, wheel_rotation = 0.0):
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(wheel_rotation, 0,1,0)
    glRotatef(angle, 0, 0, 1)
    glColor3f(0.1, 0.1, 0.1)
    glutSolidTorus(width / 2.0, radius, 12, 24)

    # raios do pneu
    for i in range(5):
        glPushMatrix()
        glRotatef(90, 0,1,0)
        glRotatef(i * 360 / 5, 1, 0, 0)
        glColor3f(0.8, 0.8, 0.8)
        glTranslatef(0, 0, 0) 
        glScalef(0.05, radius*2, 0.05)
        glutSolidCube(1.0)
        glPopMatrix()
    glPopMatrix()

def draw_car_wheels(car_size=(5.5, 2.5, 4.0), wheel_radius=0.7, wheel_width=0.4):
    global lift, wheel_angle
    length, width, height = car_size
    front_wheel_radius = wheel_radius
    back_wheel_radius = wheel_radius + 0.2

    y_pos_front = -height / 2 
    y_pos_back  = -height / 2

    x_offset_front = -length + front_wheel_radius * 2
    x_offset_back  = length - back_wheel_radius * 2
    z_offset = width - wheel_width / 2
    # tras
    draw_wheel(pos=(x_offset_back, y_pos_back + lift, z_offset), radius=back_wheel_radius, width=wheel_width, angle=wheel_angle)
    draw_wheel(pos=(x_offset_back, y_pos_back + lift, -z_offset), radius=back_wheel_radius, width=wheel_width, angle=wheel_angle)
    # frente
    draw_wheel(pos=(x_offset_front, y_pos_front + lift, z_offset), radius=front_wheel_radius, width=wheel_width, angle=wheel_angle, wheel_rotation=steering_angle)
    draw_wheel(pos=(x_offset_front, y_pos_front + lift, -z_offset), radius=front_wheel_radius, width=wheel_width, angle=wheel_angle, wheel_rotation=steering_angle)


def draw_car_door(pos = (0,0,0), size = (2.5,2.0,0.1), color = (0.8,0.1,0.1), angle = 0.0, side="left"):
    
    global left_door_angle, right_door_angle, left_door_open, right_door_open

    t = glfw.get_time()
    length, height, thickness = size
    DOOR_SPEED = 90.0  # degrees per second
    door_max_angle = 70

    if not hasattr(draw_car_door, "last_t_left"):
        draw_car_door.last_t_left = t
    if not hasattr(draw_car_door, "last_t_right"):
        draw_car_door.last_t_right = t

    if side == "left":
        dt = t - draw_car_door.last_t_left
        draw_car_door.last_t_left = t
        if left_door_open and left_door_angle < door_max_angle:
            left_door_angle += DOOR_SPEED * dt
            if left_door_angle > door_max_angle: left_door_angle = door_max_angle
        elif not left_door_open and left_door_angle > 0:
            left_door_angle -= DOOR_SPEED * dt
            if left_door_angle < 0: left_door_angle = 0
        angle = -left_door_angle
    else:  # right
        dt = t - draw_car_door.last_t_right
        draw_car_door.last_t_right = t
        if right_door_open and right_door_angle < door_max_angle:
            right_door_angle += DOOR_SPEED * dt
            if right_door_angle > door_max_angle: right_door_angle = door_max_angle
        elif not right_door_open and right_door_angle > 0:
            right_door_angle -= DOOR_SPEED * dt
            if right_door_angle < 0: right_door_angle = 0
        angle = right_door_angle

    glPushMatrix()
    glTranslatef(*pos)

    glTranslatef(-length, 0, 0)
    glRotatef(angle, 0,1,0)
    glTranslatef(length/2, 0, 0)

    glColor3f(*color)
    glScalef(length/2, height/2, thickness/2)
    glutSolidCube(2.0)
    glPopMatrix()

def draw_steering_wheel(pos, radius=0.5, thickness=0.05, color=(0.1,0.1,0.1)):
    global steering_wheel_angle
    glPushMatrix()
    
    # volante
    glTranslatef(*pos)
    glRotatef(90, 0,1,0)
    glRotatef(steering_wheel_angle, 0,0,1)
    glColor3f(*color)
    glutSolidTorus(thickness / 2.0, radius, 12, 24) 

    # raios do volante
    for i in range(3):
        glPushMatrix()
        glRotatef(i * 120, 0, 0, 1)
        glTranslatef(radius / 2.0, 0, 0)
        glScalef(radius, thickness / 2.0, thickness / 2.0)
        glutSolidCube(1.0)
        glPopMatrix()
    glPopMatrix()
    
    # cilindro central
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(90, 0,1,0)
    glRotatef(90,1,0,0)
    glutSolidCylinder(thickness / 2.0, radius*3,12,1)
    glPopMatrix()

def draw_car(car_color=(0.596,0.729,0.835), car_size=(5.5, 2.5, 4.0)):
    global car_x, car_y, car_z
    global car_speed, wheel_angle, car_direction


    length = car_size[0]
    height = car_size[1]
    width = car_size[2]

    # car_direction_rad = radians(car_direction)

    # car_x -= car_speed * cos(-car_direction_rad)
    # car_z -= car_speed * sin(-car_direction_rad)

    # wheel_radius = 0.7
    # wheel_angle += (car_speed / (2 * 3.1415 * wheel_radius)) * 360.0

    # car_speed *= 0.95

    glPushMatrix()
    glColor3f(*car_color)
    glTranslatef(car_x, car_y + lift, car_z)
    glRotatef(car_direction, 0, 1, 0)

    # parte de tras
    back_length = length * 0.25
    glPushMatrix()
    glTranslatef(length/2 + back_length, 0, 0)
    glScalef(back_length, height/2, width/2)
    glutSolidCube(2.0)
    glPopMatrix()

    # parte da frente
    front_length = length * 0.25
    glPushMatrix()
    glTranslatef(-length + front_length, 0, 0)
    glScalef(front_length, height/2, width/2)
    glutSolidCube(2.0)
    glPopMatrix()
    
    thickness = 0.05

    # base do carro
    glPushMatrix()
    glColor3f(*car_color)
    glTranslatef(0.0, -height / 2.0 + thickness / 2.0, 0.0)
    glScalef(length/2, thickness/2, width/2)
    glutSolidCube(2.0)
    glPopMatrix()

    door_side_length = 0.6
    fixed_length_car_side = 1.0 - door_side_length
    # laterais do carro
    # lateral esquerda
    glPushMatrix()
    glTranslatef(length * (door_side_length / 2.0), 0.0, width / 2.0 - thickness / 2.0)
    glScalef(length * fixed_length_car_side / 2.0, height / 2.0, thickness / 2.0)
    glutSolidCube(2.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(length * (door_side_length / 2.0), 0.0, -width / 2.0 - thickness / 2.0)
    glScalef(length * fixed_length_car_side / 2.0, height / 2.0, thickness / 2.0)
    glutSolidCube(2.0)
    glPopMatrix()

    # esquerda porta
    draw_car_door(
        pos = (-length * (fixed_length_car_side / 2.0) + length * door_side_length / 2.0, 0.0, -width / 2.0 + thickness / 2.0),
        size = (length * door_side_length, height, thickness),
        color = car_color,
        angle = right_door_angle,
        side = "right"
    )

    # direita porta
    draw_car_door(
        pos = (-length * (fixed_length_car_side / 2.0) + length * door_side_length / 2.0, 0.0, width / 2.0 - thickness / 2.0),
        size = (length * door_side_length, height, thickness),
        color = car_color,
        angle = left_door_angle,
        side = "left"
    )

    draw_steering_wheel(pos=( -length / 4.0 - 1, height / 2.0, 0.0))


    # frente e tras do carro

    for car_end in [-1,1]:
        glPushMatrix()
        glColor3f(*car_color)

        glTranslatef(length / 2 * car_end, 0.0, 0.0)
        glScalef(thickness / 2, height / 2, width / 2.0)
        glutSolidCube(2.0)
        glPopMatrix()

    # rodas
    draw_car_wheels(car_size = car_size)

    glPopMatrix()

def update_car():
    global car_speed, steering_angle, wheel_angle, car_x, car_z, car_direction

    # menor
    if abs(car_speed) < 0.001:
       return

    wheel_radius = 0.7
    wheel_angle += (car_speed / (2 * 3.1415 * wheel_radius)) * 360.0

    car_direction_rad = radians(car_direction)
    steering_rad = radians(steering_angle)

    L = 5.5  # distância entre eixos
    car_direction += degrees((car_speed / L) * tan(steering_rad))
    car_x -= car_speed * cos(-car_direction_rad - steering_rad)
    car_z -= car_speed * sin(-car_direction_rad - steering_rad)
    car_speed *= 0.95

def draw_porta_garagem(x,y,z,comprimento = 7.5, altura = 5,faixas = 10):
    global ABRIR,ANGLE_GARAGE, last_t
    glPushMatrix()
    glNormal3f(0.0, 1.0, 0.0) 
    glTranslate(x,y,z) #posição dada
    #glTranslatef(0.0, altura/2, 0.0)  # posiciona acima do chão

    #começa abrir e fechar
    #--------------------------------------//------------------------------------------
    #mecanismo de abrir e fechar a porta
    if ABRIR and ANGLE_GARAGE <90:
        # gira em torno do eixo superior
        t = glfw.get_time()
        ANGLE_GARAGE += 30.0 * max(0.0, t - last_t)
        last_t = t
    elif not ABRIR and ANGLE_GARAGE > 0:
        t = glfw.get_time()
        ANGLE_GARAGE -= 30.0 * max(0.0, t - last_t)
        last_t = t 
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
    draw_porta_garagem(0,0,0)
    update_car()
    draw_car()

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
    global left_door_open, right_door_open, steering_wheel_angle, car_speed, car_direction, steering_angle
    
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
    elif key == b'm':
        global last_t
        last_t = glfw.get_time()    #pega o tempo que começou o sinal
        ABRIR = not ABRIR
    elif key == b'p':
        eye_z -= 3
    elif key == b'o':
        eye_z += 3
    
    # portas carroww
    elif key == b'h':  # direita porta
        right_door_open = not right_door_open
    elif key == b'g':  # esquerda porta
        left_door_open = not left_door_open

    elif key == b'i':
        car_speed = 0.2
    elif key == b'k':
        car_speed = -0.2
    elif key == b'j':
        steering_angle += STEERING_SPEED
        if steering_angle > MAX_STEERING:
            steering_angle = MAX_STEERING
    elif key == b'l':
        steering_angle -= STEERING_SPEED
        if steering_angle < -MAX_STEERING:
            steering_angle = -MAX_STEERING

    elif key in (b'\x1b', b'q'):  # ESC or q
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
