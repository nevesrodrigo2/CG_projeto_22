import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import *

import var_globals

class Car:
    """
    Classe que representa o carro na cena 3D.
    """
    # -------------------------------------------------------------------------------------------------------------------------- #
    # camera dentro carro
    car_camera = False
    antigo_eye = (0.0, 5.0, 14.0)
    antigo_l_eye = (0.0, 5.0, 0.0)
    # -------------------------------------------------------------------------------------------------------------------------- #
    # carro state
    car_speed = 0.0
    acceleration = 0.2
    car_direction = 00.0
    car_x = 0.0
    car_y = 1.0
    car_z = -20.0
    left_door_angle = 0.0
    right_door_angle = 0.0
    left_door_open = False
    right_door_open = False
    lift = 1
    wheel_angle = 0.0
    steering_wheel_angle = 0.0
    steering_angle = 0.0  
    thickness = 0.05
    last_t_left = 0.0
    last_t_right = 0.0
    MAX_STEERING = 30.0   
    STEERING_SPEED = 5.0   
    DOOR_SPEED = 90.0
    DOOR_MAX_ANGLE = 70
    # -------------------------------------------------------------------------------------------------------------------------- #

    def set_material_carpaint(self,color=(0.6, 0.1, 0.1)):
        """
        Define o material para a pintura do carro com a cor especificada.
        """
        r, g, b = color
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [r*0.2, g*0.2, b*0.2, 1])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [r, g, b, 1])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.9, 0.9, 0.9, 1])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 120.0)

    def set_material_rubber(self):
        """
        Define o material para a borracha (pneus, volante).
        """
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.02, 0.02, 0.02, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [0.05, 0.05, 0.05, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 5.0)

    def set_material_tire_metal(self):
        """
        Define o material para o metal das jantes dos pneus.
        """
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  [0.6, 0.6, 0.6, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)

    def draw_wheel(self, pos=(0,0,0), radius=0.7, width=0.4, angle=0.0, wheel_rotation=0.0):
        """
        Desenha uma roda do carro com posição, raio, largura, angulo especificados.
        """
        glPushMatrix()
        self.set_material_rubber()
        glTranslatef(*pos)
        glRotatef(wheel_rotation, 0,1,0)
        glRotatef(angle, 0, 0, 1)
        glutSolidTorus(width / 2.0, radius, 12, 24)

        # jantes do pneu
        self.set_material_tire_metal()
        for i in range(5):
            glPushMatrix()
            glRotatef(90, 0,1,0)
            glRotatef(i * 360 / 5, 1, 0, 0)
            glTranslatef(0, 0, 0)
            glScalef(0.05, radius*2, 0.05)
            glutSolidCube(1.0)
            glPopMatrix()
        glPopMatrix()

    def draw_car_wheels(self, car_size=(5.5, 2.5, 4.0), wheel_radius=0.7, wheel_width=0.4):
        """
        Desenha as quatro rodas do carro com base no tamanho do carro e dimensões das rodas.
        """
        length, width, height = car_size
        front_wheel_radius = wheel_radius
        back_wheel_radius = wheel_radius + 0.2

        y_pos_front = -height / 2
        y_pos_back = -height / 2

        x_offset_front = -length + front_wheel_radius * 2
        x_offset_back  = length - back_wheel_radius * 2
        z_offset = width - wheel_width / 2

        # back wheels
        self.draw_wheel(
            pos=(x_offset_back, y_pos_back + self.lift, z_offset), 
            radius=back_wheel_radius, 
            width=wheel_width, 
            angle=self.wheel_angle
        )
        self.draw_wheel(
            pos=(x_offset_back, y_pos_back + self.lift, -z_offset), 
            radius=back_wheel_radius, 
            width=wheel_width, 
            angle=self.wheel_angle
        )
        # front wheels
        self.draw_wheel(
            pos=(x_offset_front, y_pos_front + self.lift, z_offset), 
            radius=front_wheel_radius, 
            width=wheel_width, 
            angle=self.wheel_angle, 
            wheel_rotation=self.steering_angle
        )
        self.draw_wheel(
            pos=(x_offset_front, y_pos_front + self.lift, -z_offset), 
            radius=front_wheel_radius, 
            width=wheel_width, 
            angle=self.wheel_angle, 
            wheel_rotation=self.steering_angle
        )

    def draw_car_door(self, pos=(0,0,0), size=(2.5,2.0,0.1), angle=0.0, side="left"):
        """
        Desenha uma porta do carro com posição, tamanho e ângulo especificados.
        """

        # obter o tempo atual
        t = glfw.get_time()
        length, height, thickness = size
        
        # inicializar os tempos das portas caso sejam zero
        if self.last_t_left == 0.0:
            self.last_t_left = t
        if self.last_t_right == 0.0:
            self.last_t_right = t

        # atualiza o angulo da porta dependendo do lado
        if side == "left":
            dt = t - self.last_t_left
            self.last_t_left = t
            if self.left_door_open and self.left_door_angle < self.DOOR_MAX_ANGLE:
                self.left_door_angle += self.DOOR_SPEED * dt
                if self.left_door_angle > self.DOOR_MAX_ANGLE: self.left_door_angle = self.DOOR_MAX_ANGLE
            elif not self.left_door_open and self.left_door_angle > 0:
                self.left_door_angle -= self.DOOR_SPEED * dt
                if self.left_door_angle < 0: self.left_door_angle = 0
            angle = -self.left_door_angle
        else:  # right
            dt = t - self.last_t_right
            self.last_t_right = t
            if self.right_door_open and self.right_door_angle < self.DOOR_MAX_ANGLE:
                self.right_door_angle += self.DOOR_SPEED * dt
                if self.right_door_angle > self.DOOR_MAX_ANGLE: self.right_door_angle = self.DOOR_MAX_ANGLE
            elif not self.right_door_open and self.right_door_angle > 0:
                self.right_door_angle -= self.DOOR_SPEED * dt
                if self.right_door_angle < 0: self.right_door_angle = 0
            angle = self.right_door_angle

        self.set_material_carpaint()
        glPushMatrix()
        glTranslatef(*pos)
        glTranslatef(-length, 0, 0)
        glRotatef(angle, 0,1,0)
        glTranslatef(length/2, 0, 0)
        glScalef(length/2, height/2, thickness/2)
        glutSolidCube(2.0)
        glPopMatrix()

    def draw_steering_wheel(self, pos, radius=0.5, thickness=0.05):
        """
        Desenha o volante do carro na posição especificada.
        """

        # volante (borracha)
        glPushMatrix()
        self.set_material_rubber()
        glTranslatef(*pos)
        glRotatef(90, 0,1,0)
        glRotatef(self.steering_wheel_angle, 0,0,1)
        glutSolidTorus(thickness / 2.0, radius, 12, 24)

        # raios do volante
        self.set_material_tire_metal()
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


    def draw_car(self, car_size=(5.5,2.5,4.0)):
        """
        Desenha o carro na cena 3D com o tamanho especificado.
        """

        length, height, width = car_size

        glPushMatrix()
        self.set_material_carpaint()
        glTranslatef(self.car_x, self.car_y + self.lift, self.car_z)
        glRotatef(self.car_direction, 0, 1, 0)

        # parte de tras
        back_length = length * 0.25
        glPushMatrix()
        glTranslatef(length/2 + back_length, 0, 0)
        glScalef(back_length, height/2, width/2)
        glutSolidCube(2.0)
        glPopMatrix()

        # frente
        front_length = length * 0.25
        glPushMatrix()
        glTranslatef(-length + front_length, 0, 0)
        glScalef(front_length, height/2, width/2)
        glutSolidCube(2.0)
        glPopMatrix()

        # centro
        glPushMatrix()
        glTranslatef(0.0, -height / 2.0 + self.thickness / 2.0, 0.0)
        glScalef(length/2, self.thickness/2, width/2)
        glutSolidCube(2.0)
        glPopMatrix()

        door_side_length = 0.6
        fixed_length_car_side = 1.0 - door_side_length

        # lados
        glPushMatrix()
        glTranslatef(length * (door_side_length / 2.0), 0.0, width / 2.0 - self.thickness / 2.0)
        glScalef(length * fixed_length_car_side / 2.0, height / 2.0, self.thickness / 2.0)
        glutSolidCube(2.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(length * (door_side_length / 2.0), 0.0, -width / 2.0 - self.thickness / 2.0)
        glScalef(length * fixed_length_car_side / 2.0, height / 2.0, self.thickness / 2.0)
        glutSolidCube(2.0)
        glPopMatrix()

        # doors
        # porta direita
        self.draw_car_door(pos=(-length * (fixed_length_car_side / 2.0) + length * door_side_length / 2.0, 0.0, -width / 2.0 + self.thickness / 2.0),
                           size=(length * door_side_length, height, self.thickness),
                           angle=self.right_door_angle, side="right")

        # porta esquerda
        self.draw_car_door(pos=(-length * (fixed_length_car_side / 2.0) + length * door_side_length / 2.0, 0.0, width / 2.0 - self.thickness / 2.0),
                           size=(length * door_side_length, height, self.thickness),
                           angle=self.left_door_angle, side="left")
        
        # volante
        self.draw_steering_wheel(pos=(-length / 4.0 - 1, height / 2.0, 0.0))

        # partes da frente e de trás
        for car_end in [-1, 1]:
            glPushMatrix()
            glTranslatef(length / 2 * car_end, 0.0, 0.0)
            glScalef(self.thickness / 2, height / 2, width / 2.0)
            glutSolidCube(2.0)
            glPopMatrix()

        # rodas
        self.draw_car_wheels(car_size=car_size)
        glPopMatrix()

    def update_car(self):
        """
        Atualiza a posição e direção do carro com base na velocidade e ângulo de direção.
        Também atualiza a posição da câmera se estiver no modo de câmera do carro.
        """

        # caso esteja a ser usada a camara interior do carro
        if self.car_camera:
            car_direction_rad = radians(self.car_direction -90)
            var_globals.eye_x = self.car_x
            var_globals.eye_y = self.car_y + 3
            var_globals.eye_z = self.car_z
            var_globals.leye_x = self.car_x + sin(car_direction_rad)*2
            var_globals.leye_y = var_globals.eye_y
            var_globals.leye_z = self.car_z + cos(car_direction_rad)*2
        if abs(self.car_speed) < 0.001:
            return

        # atualiza o angulo do volante e das rodas
        self.steering_wheel_angle += (self.steering_angle * 3.0 - self.steering_wheel_angle) * 0.1
        wheel_radius = 0.7
        self.wheel_angle += (self.car_speed / (2 * 3.1415 * wheel_radius)) * 360.0

        car_direction_rad = radians(self.car_direction)
        steering_rad = radians(self.steering_angle)
        L = 5.5

        # atualiza a posição e direção do carro
        self.car_direction += degrees((self.car_speed / L) * tan(steering_rad))
        self.car_x -= self.car_speed * cos(-car_direction_rad - steering_rad)
        self.car_z -= self.car_speed * sin(-car_direction_rad - steering_rad)

        # diminuiçao de velocidade
        self.car_speed *= 0.95


    def drive(self, dir: str):
        """
        Controla o movimento do carro com base na direção especificada.
        """
        if dir == "forward":
            self.car_speed = self.acceleration
        elif dir == "backward":
            self.car_speed = -self.acceleration
        elif dir == "left":
            self.steering_angle += self.STEERING_SPEED
            self.steering_angle = min(self.steering_angle, self.MAX_STEERING)
            self.steering_wheel_angle = self.steering_angle * 3.0
        elif dir == "right":
            self.steering_angle -= self.STEERING_SPEED
            self.steering_angle = max(self.steering_angle, -self.MAX_STEERING)
            self.steering_wheel_angle = self.steering_angle * 3.0

    def change_car_camera_mode(self):
        """
        Alterna entre a visão da câmera dentro e fora do carro.
        """
        self.car_camera = not self.car_camera
        if self.car_camera:
            self.antigo_eye = (var_globals.eye_x, var_globals.eye_y, var_globals.eye_z)
            self.antigo_l_eye = (var_globals.leye_x, var_globals.leye_y, var_globals.leye_z)
        else:
            var_globals.eye_x, var_globals.eye_y, var_globals.eye_z = self.antigo_eye
            var_globals.leye_x, var_globals.leye_y, var_globals.leye_z = self.antigo_l_eye

    def toggle_door(self, side: str):
        """ 
        Alterna o estado (aberto/fechado) da porta especificada. 
        """
        if side == "left":
            self.left_door_open = not self.left_door_open
        elif side == "right":
            self.right_door_open = not self.right_door_open
