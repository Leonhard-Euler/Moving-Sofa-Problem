#coding: utf-8
import math
import numpy as np
from CouchProducer import CouchProducer
from VisualHelper import VisualHelper
from Corridor import Corridor


# C:\Users\LzyRapx\PycharmProjects\untitled1\MovingSofa

class Simulator:
    def __init__(self, path, frames=100, show_error=True):
        self.path = path
        self.N = path.N
        self.poly_path = [c.to_polygon() for c in path.corridors]
        self.producer = CouchProducer(self)
        self.valid = self.producer.valid
        if not self.valid and show_error:
            print(self.producer.error_message)
        self.couch = self.producer.couch
        self.__visual = VisualHelper(self, frames)
        self.raw_area = self.couch.area
        self.area = self.raw_area - 1 / (self.N) if self.valid else 0

    def show_path(self, couch_name='couch', num_corridors=60, offset_x=0.75, offset_y=0.2):
        self.__visual.plot_path(couch_name, num_corridors, offset_x, offset_y)

    def demo_path(self, frame, offset_x=0.5, offset_y=0.2):
        self.__visual.plot_path_demo(frame, offset_x=offset_x, offset_y=offset_y)

    def show_couch(self):
        self.__visual.plot(self.couch)

    def animate(self, couch_name=None, trail=False, offset_x=0.75, offset_y=0.2):
        ani = self.__visual.animate(couch_name, trail, offset_x, offset_y)
        if couch_name is not None:
            ani.save('{}.mp4'.format(couch_name), writer= self.__visual.writer, dpi = 200)
            self.__visual.__reinit__()
        return ani

    def compare_with(self, simulatorB, nameA='A', nameB='B'):
        print('Area of {}:{}; Area of {}:{}'.format(nameA,self.area,nameB,simulatorB.area))
        self.__visual.compare(self.couch, simulatorB.couch, nameA, nameB)

class Path:
    def __init__(self, x, N, angle=math.pi / 2, ambi=False):
        self.corridors = []  # required, simulator code expects this
        self.x = x
        self.N = N
        self.angle = angle
        self.__fill_path(ambi)

    def __fill_path(self, ambi):
        for t in np.linspace(0, math.pi - self.angle, self.N):
            base = Corridor(angle=self.angle)
            base.move(self.x, t, ambi)
            self.corridors.append(base)

class RotationPaths:
    @staticmethod
    def semi_circle():
        return lambda t: np.array([0, 0])

    @staticmethod
    def hammersley(r=2 / math.pi):
        return lambda t: r * np.array([np.cos(2 * t) - 1, np.sin(2 * t)])

    @staticmethod
    def ellipse(r=0.604316547, h=0.666734694):
        return lambda t: np.array([r * np.cos(2 * t) - r, h * np.sin(2 * t)])

    @staticmethod
    def gerver():
        phi = 0.039177364790083641
        theta = 0.681301509382724894
        k = [
            np.array([-0.210322422072688751, 0.25]),
            np.array([-0.919179292771593322, 0.472406619750805465]),
            np.array([-0.613763229430251668, 0.889626479003221860]),
            np.array([-0.308347166088910014, 0.472406619750805465]),
            np.array([-1.017204036787814585, 0.25])
        ]
        a = (1.210322422072688751, -0.25)
        b = (-0.527624598026784624, 0.920258385160637622)
        c = (0.626045522848465867, -0.944750803946430751)
        d = (1.313022761424232933, -0.525382670414554437)
        e = (1.210322422072688751, 0.25)

        rot = lambda t: np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        points = lambda t: [
            np.array([a[0] * np.cos(t) + a[1] * np.sin(t) - 1,
                      -a[1] * np.cos(t) + a[0] * np.sin(t) - 0.5]),

            np.array([-0.25 * t * t + b[0] * t + b[1],
                      0.5 * t - b[0] - 1]),

            np.array([c[0] - t,
                      c[1] + t]),

            np.array([-0.5 * t + d[0] - 1,
                      -0.25 * t * t + d[0] * t + d[1]]),

            np.array([e[0] * np.cos(t) + e[1] * np.sin(t) - 0.5,
                      -e[1] * np.cos(t) + e[0] * np.sin(t) - 1])
        ]
        __x = lambda i, t: np.matmul(rot(t), points(t)[i]) + k[i]
        return lambda t: RotationPaths.romik(phi, theta, __x, t)

    @staticmethod
    def romik(phi, theta, x, t):  # x is a function, x(i,t)=x_i(t), as described in Romik's paper
        if 0 <= t < phi:
            return x(0, t)
        elif phi <= t < theta:
            return x(1, t)
        elif theta <= t <= math.pi / 2 - theta:
            return x(2, t)
        elif math.pi / 2 - theta < t <= math.pi / 2 - phi:
            return x(3, t)
        elif math.pi / 2 - phi < t <= math.pi / 2:
            return x(4, t)

    @staticmethod
    def rhf(r, h, f, N, symmetrize=False):
        return RotationPaths.rhgf(r, h, lambda t: 1, f, N, symmetrize)

    @staticmethod
    def rhgf(r, h, g, f, N, symmetrize=False):
        def __symmetrize(f):
            return lambda t: f(2 * t) if t < math.pi / 4 else f(math.pi - 2 * t)

        def __scale_f(h, f):
            sup = max([f(t) * np.sin(2 * t) for t in np.linspace(0, math.pi / 2, N)])
            if h == 0 or sup == 0:
                return lambda t: 0
            return lambda t: f(t) * h / sup

        def __scale_g(r, g):
            if g(math.pi / 2) == 0:
                return lambda t: 0
            return lambda t: (r * g(t)) / g(math.pi / 2)

        if symmetrize:
            f = __symmetrize(f)
        f = __scale_f(h, f)
        g = __scale_g(r, g)
        return lambda t: np.array([g(t) * np.cos(2 * t) - g(t), f(t) * np.sin(2 * t)])
