import numpy as np
from numpy import ndarray

from .exceptions import NegativeFloor

class Floor:
    def __init__(self, xmin:float, xmax:float, ymin:float, ymax:float):
        if xmin > xmax or ymin > ymax:
            raise NegativeFloor(xmin, xmax, ymin, ymax)
        
        self.xmin = float(xmin)
        self.xmax = float(xmax)
        self.ymin = float(ymin)
        self.ymax = float(ymax)


    def __str__(self) -> str:
        return '({} {} {} {})'.format(self.xmin, self.xmax, self.ymin, self.ymax)


    def lattice_from_delta(self, delta:float) -> ndarray:
        nx = (self.xmax - self.xmin) / delta
        nx = max(1, int(np.round(nx)))

        ny = (self.ymax - self.ymin) / delta
        ny = max(1, int(np.round(ny)))

        dx = (self.xmax - self.xmin) / nx
        x_ = np.linspace(self.xmin + dx/2, self.xmax - dx/2, nx, dtype=np.float32)
        dy = (self.ymax - self.ymin) / ny
        y_ = np.linspace(self.ymin + dy/2, self.ymax - dy/2, ny, dtype=np.float32)
        x = np.stack(np.meshgrid(x_, y_)).T

        return x
