import numpy as np
from numpy import ndarray
from .gaussian import Gaussian

class Area:
    def __init__(self, name:str, init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian, floorsize:tuple):
        self.name = name
        self.motion_num = init_prob.shape[0]
        self.init_prob = init_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian
        self.floorsize = floorsize


def create_area(name:str, floorsize:tuple) -> Area:
    nx = (floorsize[2] - floorsize[0]) / 4
    nx = max(1, int(np.round(nx)))

    ny = (floorsize[3] - floorsize[1]) / 4
    ny = max(1, int(np.round(ny)))

    n = nx * ny
    p = 1 / n

    init_prob = p * np.ones((n,), dtype=np.float32)
    tr_prob = p * np.ones((n, n), dtype=np.float32)
    dx = (floorsize[2] - floorsize[0]) / nx
    avrs_x = np.linspace(floorsize[0] + dx/2, floorsize[2] - dx/2, nx, dtype=np.float32)
    dy = (floorsize[3] - floorsize[1]) / ny
    avrs_y = np.linspace(floorsize[1] + dy/2, floorsize[3] - dy/2, ny, dtype=np.float32)
    avrs = np.stack([avrs_x, avrs_y]).T
    covars = np.ones((n, 3), dtype=np.float32)
    covars[:,1] = np.zeros((n,), dtype=np.float32)

    return Area(
        name,
        init_prob,
        tr_prob,
        Gaussian(avrs, covars),
        floorsize
    )
