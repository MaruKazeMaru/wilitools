import numpy as np
from numpy import ndarray

from .floor import Floor
from .gaussian import Gaussian
from .rand import uniform_cube

class Area:
    def __init__(
        self, name:str, floor:Floor,
        init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian,
        sample:ndarray, dens_sample:ndarray
    ):
        # meta
        self.name = name
        self.floor = floor

        # hmm parameters
        self.motion_num = init_prob.shape[0]
        self.init_prob = init_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian

        # transition failure prob
        self.sample_size = dens_sample.shape[0]
        self.sample = sample
        self.dens_sample = dens_sample


    def __str__(self) -> str:
        s_g = self.gaussian.__str__()
        s_t = self.tr_prob.__str__()

        h = '              '
        s = 'name        : %s\n' % self.name \
          + 'floorsize   : {}\n'.format(self.floor) \
          + 'motion_num  : %d\n' % self.motion_num \
          + 'init_prob   : {}\n'.format(self.init_prob) \
          + 'tr_prob     : ' + s_t.replace('\n', '\n' + h) + '\n' \
          + 'gaussian    : \n' + s_g + '\n' \
          + 'sample_size : %d' % self.sample_size
        return s


def create_area(name:str, floor:Floor, sample_size:int=300) -> Area:
    # hmm parameters
    _a = floor.lattice_from_delta(4)
    avrs = _a.reshape((_a.shape[0] * _a.shape[1], 2))

    n = avrs.shape[0]
    p = 1 / n

    init_prob = p * np.ones((n,), dtype=np.float32)
    tr_prob = p * np.ones((n, n), dtype=np.float32)
    covars = np.ones((n, 3), dtype=np.float32)
    covars[:,1] = np.zeros((n,), dtype=np.float32)

    # transition failure prob
    sample = uniform_cube(n, sample_size)
    dens_sample = np.ones((sample_size,), dtype=np.float32)

    return Area(
        name, floor,
        init_prob, tr_prob, Gaussian(avrs, covars),
        sample, dens_sample
    )
