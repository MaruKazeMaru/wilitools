# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np

from ._exceptions import NegativeFloor

class Floor:
    def __init__(self, x_min:float, x_max:float, y_min:float, y_max:float):
        if x_min > x_max or y_min > y_max:
            raise NegativeFloor(x_min, x_max, y_min, y_max)
        
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)


    def __str__(self) -> str:
        return '({} {} {} {})'.format(self.x_min, self.x_max, self.y_min, self.y_max)


    def lattice_from_delta(self, delta:float) -> np.ndarray:
        nx = (self.x_max - self.x_min) / delta
        nx = max(1, int(np.round(nx)))

        ny = (self.y_max - self.y_min) / delta
        ny = max(1, int(np.round(ny)))

        dx = (self.x_max - self.x_min) / nx
        x_ = np.linspace(self.x_min + dx/2, self.x_max - dx/2, nx, dtype=np.float32)
        dy = (self.y_max - self.y_min) / ny
        y_ = np.linspace(self.y_min + dy/2, self.y_max - dy/2, ny, dtype=np.float32)
        x = np.stack(np.meshgrid(x_, y_)).T

        return x
