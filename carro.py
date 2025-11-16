import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys, os
from math import *

import var_globals

class Car:
    # -------------------------------------------------------------------------------------------------------------------------- #
    # camera dentro carro
    CameraDeCarro = False
    antigoeye = (0.0, 5.0, 14.0)
    antigoleye = (0.0, 5.0, 0.0)
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
    MAX_STEERING = 30.0   
    STEERING_SPEED = 5.0   
    last_t_left = 0.0
    last_t_right = 0.0
    # -------------------------------------------------------------------------------------------------------------------------- #


    def draw_wheel(self, pos=(0,0,0), radius=0.7, width=0.4, angle=0.0, wheel_rotation=0.0):
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

    def draw_car_wheels(self, car_size=(5.5, 2.5, 4.0), wheel_radius=0.7, wheel_width=0.4):
        length, width, height = car_size
        front_wheel_radius = wheel_radius
        back_wheel_radius = wheel_radius + 0.2

        y_pos_front = -height / 2
        y_pos_back = -height / 2

        x_offset_front = -length + front_wheel_radius * 2
        x_offset_back  = length - back_wheel_radius * 2
        z_offset = width - wheel_width / 2

        # back wheels
        self.draw_wheel(pos=(x_offset_back, y_pos_back + self.lift, z_offset), radius=back_wheel_radius, width=wheel_width, angle=self.wheel_angle)
        self.draw_wheel(pos=(x_offset_back, y_pos_back + self.lift, -z_offset), radius=back_wheel_radius, width=wheel_width, angle=self.wheel_angle)
        # front wheels
        self.draw_wheel(pos=(x_offset_front, y_pos_front + self.lift, z_offset), radius=front_wheel_radius, width=wheel_width, angle=self.wheel_angle, wheel_rotation=self.steering_angle)
        self.draw_wheel(pos=(x_offset_front, y_pos_front + self.lift, -z_offset), radius=front_wheel_radius, width=wheel_width, angle=self.wheel_angle, wheel_rotation=self.steering_angle)

    def draw_car_door(self, pos=(0,0,0), size=(2.5,2.0,0.1), color=(0.8,0.1,0.1), angle=0.0, side="left"):
        t = glfw.get_time()
        length, height, thickness = size
        DOOR_SPEED = 90.0
        door_max_angle = 70

        if self.last_t_left == 0.0:
            self.last_t_left = t
        if self.last_t_right == 0.0:
            self.last_t_right = t

        if side == "left":
            dt = t - self.last_t_left
            self.last_t_left = t
            if self.left_door_open and self.left_door_angle < door_max_angle:
                self.left_door_angle += DOOR_SPEED * dt
                if self.left_door_angle > door_max_angle: self.left_door_angle = door_max_angle
            elif not self.left_door_open and self.left_door_angle > 0:
                self.left_door_angle -= DOOR_SPEED * dt
                if self.left_door_angle < 0: self.left_door_angle = 0
            angle = -self.left_door_angle
        else:  # right
            dt = t - self.last_t_right
            self.last_t_right = t
            if self.right_door_open and self.right_door_angle < door_max_angle:
                self.right_door_angle += DOOR_SPEED * dt
                if self.right_door_angle > door_max_angle: self.right_door_angle = door_max_angle
            elif not self.right_door_open and self.right_door_angle > 0:
                self.right_door_angle -= DOOR_SPEED * dt
                if self.right_door_angle < 0: self.right_door_angle = 0
            angle = self.right_door_angle

        glPushMatrix()
        glTranslatef(*pos)
        glTranslatef(-length, 0, 0)
        glRotatef(angle, 0,1,0)
        glTranslatef(length/2, 0, 0)
        glColor3f(*color)
        glScalef(length/2, height/2, thickness/2)
        glutSolidCube(2.0)
        glPopMatrix()

    def draw_steering_wheel(self, pos, radius=0.5, thickness=0.05, color=(0.1,0.1,0.1)):
        glPushMatrix()
        glTranslatef(*pos)
        glRotatef(90, 0,1,0)
        glRotatef(self.steering_wheel_angle, 0,0,1)
        glColor3f(*color)
        glutSolidTorus(thickness / 2.0, radius, 12, 24)

        for i in range(3):
            glPushMatrix()
            glRotatef(i * 120, 0, 0, 1)
            glTranslatef(radius / 2.0, 0, 0)
            glScalef(radius, thickness / 2.0, thickness / 2.0)
            glutSolidCube(1.0)
            glPopMatrix()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(*pos)
        glRotatef(90, 0,1,0)
        glRotatef(90,1,0,0)
        glutSolidCylinder(thickness / 2.0, radius*3,12,1)
        glPopMatrix()

    def draw_car(self, car_color=(0.596,0.729,0.835), car_size=(5.5,2.5,4.0)):
        length, height, width = car_size

        glPushMatrix()
        glColor3f(*car_color)
        glTranslatef(self.car_x, self.car_y + self.lift, self.car_z)
        glRotatef(self.car_direction, 0, 1, 0)

        # rear
        back_length = length * 0.25
        glPushMatrix()
        glTranslatef(length/2 + back_length, 0, 0)
        glScalef(back_length, height/2, width/2)
        glutSolidCube(2.0)
        glPopMatrix()

        # front
        front_length = length * 0.25
        glPushMatrix()
        glTranslatef(-length + front_length, 0, 0)
        glScalef(front_length, height/2, width/2)
        glutSolidCube(2.0)
        glPopMatrix()

        thickness = 0.05
        # base
        glPushMatrix()
        glColor3f(*car_color)
        glTranslatef(0.0, -height / 2.0 + thickness / 2.0, 0.0)
        glScalef(length/2, thickness/2, width/2)
        glutSolidCube(2.0)
        glPopMatrix()

        door_side_length = 0.6
        fixed_length_car_side = 1.0 - door_side_length

        # sides
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

        # doors
        self.draw_car_door(pos=(-length * (fixed_length_car_side / 2.0) + length * door_side_length / 2.0, 0.0, -width / 2.0 + thickness / 2.0),
                           size=(length * door_side_length, height, thickness),
                           color=car_color, angle=self.right_door_angle, side="right")

        self.draw_car_door(pos=(-length * (fixed_length_car_side / 2.0) + length * door_side_length / 2.0, 0.0, width / 2.0 - thickness / 2.0),
                           size=(length * door_side_length, height, thickness),
                           color=car_color, angle=self.left_door_angle, side="left")

        self.draw_steering_wheel(pos=(-length / 4.0 - 1, height / 2.0, 0.0))

        # front & rear end cubes
        for car_end in [-1, 1]:
            glPushMatrix()
            glColor3f(*car_color)
            glTranslatef(length / 2 * car_end, 0.0, 0.0)
            glScalef(thickness / 2, height / 2, width / 2.0)
            glutSolidCube(2.0)
            glPopMatrix()

        # wheels
        self.draw_car_wheels(car_size=car_size)
        glPopMatrix()

    def update_car(self):
        if self.CameraDeCarro:
            car_direction_rad = radians(self.car_direction -90)
            var_globals.eye_x = self.car_x
            var_globals.eye_y = self.car_y + 3
            var_globals.eye_z = self.car_z
            var_globals.leye_x = self.car_x + sin(car_direction_rad)*2
            var_globals.leye_y = var_globals.eye_y
            var_globals.leye_z = self.car_z + cos(car_direction_rad)*2
        if abs(self.car_speed) < 0.001:
            return

        self.steering_wheel_angle += (self.steering_angle * 3.0 - self.steering_wheel_angle) * 0.1
        wheel_radius = 0.7
        self.wheel_angle += (self.car_speed / (2 * 3.1415 * wheel_radius)) * 360.0

        car_direction_rad = radians(self.car_direction)
        steering_rad = radians(self.steering_angle)
        L = 5.5

        self.car_direction += degrees((self.car_speed / L) * tan(steering_rad))
        self.car_x -= self.car_speed * cos(-car_direction_rad - steering_rad)
        self.car_z -= self.car_speed * sin(-car_direction_rad - steering_rad)
        self.car_speed *= 0.95


    def drive(self, dir: str):
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
        self.CameraDeCarro = not self.CameraDeCarro
        if self.CameraDeCarro:
            self.antigoeye = (var_globals.eye_x, var_globals.eye_y, var_globals.eye_z)
            self.antigoleye = (var_globals.leye_x, var_globals.leye_y, var_globals.leye_z)
        else:
            var_globals.eye_x, var_globals.eye_y, var_globals.eye_z = self.antigoeye
            var_globals.leye_x, var_globals.leye_y, var_globals.leye_z = self.antigoleye

    def toggle_door(self, side: str):
        if side == "left":
            self.left_door_open = not self.left_door_open
        elif side == "right":
            self.right_door_open = not self.right_door_open
