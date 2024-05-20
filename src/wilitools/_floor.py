# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np

class Floor:
    def __init__(self, x_min:float, x_max:float, y_min:float, y_max:float):
        err_msgs = []
        if x_min > x_max:
            err_msgs.append('x_min > x_max ( x_min={}, x_max={})'.format(x_min, x_max))
        if y_min > y_max:
            err_msgs.append('y_min > y_max ( y_min={}, y_max={})'.format(y_min, y_max))
        if len(err_msgs) > 0:
            raise ValueError(', '.join(err_msgs))
        
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)


    def __str__(self) -> str:
        return '({} {} {} {})'.format(self.x_min, self.x_max, self.y_min, self.y_max)


    def get_lattice(self, delta:float) -> np.ndarray:
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
