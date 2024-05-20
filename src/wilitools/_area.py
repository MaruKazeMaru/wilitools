# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np

from ._floor import Floor
from ._gaussian import Gaussian
from ._rand import uniform_cube

class Area:
    def __init__(
        self, floor:Floor,
        start_prob:np.ndarray, tr_prob:np.ndarray, gaussian:Gaussian,
        miss_probs:np.ndarray, dens_miss_probs:np.ndarray,
        name:str=None
    ):
        # meta
        self.name = name
        self.floor = floor

        # hmm parameters
        self.motion_num = start_prob.shape[0]
        self.start_prob = start_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian

        # transition miss prob
        self.sample_size = dens_miss_probs.shape[0]
        self.miss_probs = miss_probs
        self.dens_miss_probs = dens_miss_probs # probability density of miss_probs


    def __str__(self) -> str:
        s_g = self.gaussian.__str__()
        s_t = self.tr_prob.__str__()

        h = '             '
        s = 'name       : %s\n' % self.name \
          + 'floor      : {}\n'.format(self.floor) \
          + 'motion_num : %d\n' % self.motion_num \
          + 'start_prob : {}\n'.format(self.start_prob) \
          + 'tr_prob    : ' + s_t.replace('\n', '\n' + h) + '\n' \
          + 'gaussian   : \n' + s_g + '\n' \
          + 'sample_num : %d' % self.sample_size
        return s


def create_default_area(floor:Floor, name:str = None, sample_num:int=300) -> Area:
    # hmm parameters
    _a = floor.get_lattice(4)
    avrs = _a.reshape((_a.shape[0] * _a.shape[1], 2))

    n = avrs.shape[0]
    p = 1 / n

    init_prob = p * np.ones((n,), dtype=np.float32)
    tr_prob = p * np.ones((n, n), dtype=np.float32)
    covars = np.ones((n, 3), dtype=np.float32)
    covars[:,1] = np.zeros((n,), dtype=np.float32)

    # transition miss prob
    miss_probs = uniform_cube(n, sample_num)
    dens_miss_probs = np.ones((sample_num,), dtype=np.float32)

    return Area(
        floor,
        init_prob, tr_prob, Gaussian(avrs, covars),
        miss_probs, dens_miss_probs,
        name = name
    )
