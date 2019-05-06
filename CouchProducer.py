#coding:utf-8
from shapely.geometry import Polygon
from shapely.geometry import GeometryCollection

class CouchProducer:
    def __init__(self, simulator):
        self.N = len(simulator.poly_path)
        self.__pathObj = simulator.path.corridors
        self.path = simulator.poly_path
        self.__make_couch()
        self.__validate_couch()

    def __make_couch(self):
        self.couch = self.__intersect_in_pairs(self.path)

    def __clear_collection(self, result):
        if result.geom_type == 'Polygon':
            return result
        result = GeometryCollection([P for P in result if P.geom_type == 'Polygon'])
        return result[0] if len(result) == 1 else result

    def __intersect_in_pairs(self, to_intersect):
        if (len(to_intersect) == 1):
            return to_intersect[0]
        l = []
        for idx, corridor in enumerate(to_intersect):
            if (idx % 2 != 0): continue
            result = None
            if idx + 1 == len(to_intersect):
                result = corridor  # has no pair
            else:
                result = corridor.intersection(to_intersect[idx + 1])
            l.append(result)
        return self.__intersect_in_pairs(l)

    def __validate_couch(self):
        self.valid = True
        self.couch = self.__clear_collection(self.couch)

        last = self.__pathObj[-1]
        self.not_turned = self.couch.intersection(last.top()).area
        if self.not_turned >= 1 / self.N:
            self.valid = False
            self.error_message = 'An area of {} has not yet turned corner.'.format(self.not_turned)

        if self.couch.geom_type != 'Polygon':
            self.valid = False
            self.error_message = 'The resulting couch is not a single piece.'
