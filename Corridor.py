#coding:utf-8
from shapely.geometry import Polygon # pip3 install shapely
import numpy as np
import math

class Corridor:
    def __init__(self, angle,length=10):
        self.angle = angle
        self.vertices = dict()
        self.vertices["INNER_CENTER"] = np.array([0, 0])
        self.vertices["INNER_LEFT"] = np.array([-1 * length, 0])
        self.vertices["OUTER_LEFT"] = np.array([-1 * length, 1])
        self.vertices["INNER_RIGHT"] = -1 * length * np.array([math.cos(angle), math.sin(angle)])
        self.vertices["OUTER_RIGHT"] = self.__travel(self.vertices["INNER_RIGHT"],self.__right_vec(),1)
        self.vertices["OUTER_CENTER"] = self.__from_intercept(self.vertices["OUTER_RIGHT"], math.tan(angle))
        self.vertices["MID"] = self.__from_intercept(self.vertices["INNER_RIGHT"], math.tan(angle))

    def __get_x_intercept(self, p, slope):
        return np.array([p[0] - p[1] / slope, 0])

    def __right_vec(self):
        if self.angle == math.pi / 2:
            return np.array([1, 0])
        slope = -1 / math.tan(self.angle)
        unnormed_vec = self.__get_x_intercept(self.vertices["INNER_RIGHT"], slope) - self.vertices["INNER_RIGHT"]
        normed = self.__normalize(unnormed_vec)
        return normed if self.angle > math.pi / 2 else -1 * normed

    def __travel(self, start, vec, distance):
        return start + distance * vec

    def __normalize(self, v):
        return v / np.linalg.norm(v)

    def __from_intercept(self, p, slope):
        x = (1 - p[1]) / slope + p[0]
        return np.array([x, 1])

    def move(self, x, t, clockwise=False):  # 0 <= t <= math.pi- corridor angle
        T = -t if clockwise else t
        cos, sin = np.cos(T), np.sin(T)
        rot_matrix = np.array([[cos, -sin], [sin, cos]])
        for key, vert in self.vertices.items():
            self.vertices[key] = np.matmul(rot_matrix, vert) + x(t)

    def top(self):
        return Polygon([self.vertices["OUTER_LEFT"],
                        self.vertices["MID"],
                        self.vertices["INNER_CENTER"],
                        self.vertices["INNER_LEFT"],
                        self.vertices["OUTER_LEFT"]])

    def to_polygon(self):
        return Polygon([self.vertices["INNER_CENTER"],
                        self.vertices["INNER_LEFT"],
                        self.vertices["OUTER_LEFT"],
                        self.vertices["MID"],
                        self.vertices["OUTER_CENTER"],
                        self.vertices["OUTER_RIGHT"],
                        self.vertices["INNER_RIGHT"],
                        self.vertices["INNER_CENTER"]])
