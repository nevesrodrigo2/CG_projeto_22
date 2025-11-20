from OpenGL.GL import *
import math

def draw_cube(size=1.0):
    s = size / 2.0
    glBegin(GL_QUADS)

    # +X face
    glNormal3f(1, 0, 0)
    glVertex3f( s,-s,-s)
    glVertex3f( s, s,-s)
    glVertex3f( s, s, s)
    glVertex3f( s,-s, s)

    # -X face
    glNormal3f(-1, 0, 0)
    glVertex3f(-s,-s, s)
    glVertex3f(-s, s, s)
    glVertex3f(-s, s,-s)
    glVertex3f(-s,-s,-s)

    # +Y face
    glNormal3f(0, 1, 0)
    glVertex3f(-s, s,-s)
    glVertex3f(-s, s, s)
    glVertex3f( s, s, s)
    glVertex3f( s, s,-s)

    # -Y face
    glNormal3f(0, -1, 0)
    glVertex3f(-s,-s, s)
    glVertex3f(-s,-s,-s)
    glVertex3f( s,-s,-s)
    glVertex3f( s,-s, s)

    # +Z face
    glNormal3f(0, 0, 1)
    glVertex3f(-s,-s, s)
    glVertex3f( s,-s, s)
    glVertex3f( s, s, s)
    glVertex3f(-s, s, s)

    # -Z face
    glNormal3f(0, 0,-1)
    glVertex3f( s,-s,-s)
    glVertex3f(-s,-s,-s)
    glVertex3f(-s, s,-s)
    glVertex3f( s, s,-s)

    glEnd()

def draw_torus(inner_radius, outer_radius, nsides, rings):
    for i in range(rings):
        glBegin(GL_QUAD_STRIP)
        for j in range(nsides+1):
            for k in [i, i+1]:
                s = (k % rings + 0.5) / rings * 2 * math.pi
                t = j / nsides * 2 * math.pi
                x = (outer_radius + inner_radius * math.cos(t)) * math.cos(s)
                y = (outer_radius + inner_radius * math.cos(t)) * math.sin(s)
                z = inner_radius * math.sin(t)
                glVertex3f(x, y, z)
        glEnd()