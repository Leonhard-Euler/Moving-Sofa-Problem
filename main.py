import unittest
import math
import numpy as np
from MovingSofa import Simulator
from MovingSofa import Path
from MovingSofa import RotationPaths

class UnitTest(unittest.TestCase):
    def test_semi_circle(self): # 半圆
        path = Path(x=RotationPaths.semi_circle(),N=100000)
        simulator = Simulator(path=path, show_error=True)
        print("\nsemi_circle:")
        #  1.570786326827179
        print("Simulator area = ", simulator.area)
        simulator.show_path(couch_name='SemiCircle')
        self.assertAlmostEqual(simulator.area, math.pi / 2, delta=precision)

    def test_hammersley(self):
        r = 2 / math.pi  # Hammersley
        actual_area = math.pi / 2 + r * (2 - math.pi / 2 * r)
        path = Path(x=RotationPaths.hammersley(r),N=40000)
        simulator = Simulator(path=path, show_error=True)
        print("\nhammersley:")
        # 2.2074070147932088
        print("Simulator.area = ", simulator.area)
        self.assertAlmostEqual(simulator.area, actual_area, delta=precision)
        # places could be increased if N is increased
        # but want to keep runtime low
    def test_gerver(self):
        gerver_area = 2.21953166
        path = Path(x=RotationPaths.gerver(),N=45000)
        simulator = Simulator(path=path, show_error=False)
        print("\ngerver:")
        # 2.2195225309390785
        print("Simulator.area = ", simulator.area)
        simulator.show_path(couch_name='gerver') # 输出pdf
        simulator.animate(couch_name='gerver') # 输出mp4
        self.assertAlmostEqual(simulator.area, gerver_area, delta=precision)

    def test_failure(self):
        r = 1.000001
        path = Path(x=RotationPaths.hammersley(r), N=10000)
        simulator = Simulator(path=path, show_error=False)
        print("\nfailure")
        print("simulator = ", simulator)
        print("simulator = ", simulator.area)
        self.assertFalse(simulator.valid)

precision = 0.00001
suite = unittest.TestLoader().loadTestsFromTestCase(UnitTest)
unittest.TextTestRunner(verbosity=2).run(suite)
