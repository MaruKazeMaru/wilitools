# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np
from numpy import ndarray

class Gaussian:
    def __init__(self, avrs:ndarray, covars:ndarray):
        self.avrs = avrs
        self.covars = covars

        # cache
        self._dets:ndarray = None
        self._divs:ndarray = None


    def __str__(self) -> str:
        s_a = self.avrs.__str__()
        s_c = self.covars.__str__()
        h = '         '
        s = 'avrs   : ' + s_a.__str__().replace('\n', '\n' + h) + '\n' \
          + 'covars : ' + s_c.__str__().replace('\n', '\n' + h)
        return s


    def weighted(self, x:ndarray, weight:ndarray) -> float | ndarray:
        if self._divs is None:
            self._dets = self.covars[:,0] * self.covars[:,2] - self.covars[:,1] * self.covars[:,1]
            self._divs = 2.0 * np.pi * self._dets

        x_num = 1
        x_shape = [n for n in x.shape]
        x_shape = x_shape[:-1]
        for n in x_shape:
            x_num *= n

        motion_num = self.avrs.shape[0]

        x_ = x.reshape((x_num, 1, 2)) - self.avrs.reshape((1, motion_num, 2))
        # calc (x-myu)^T Sigma^-1 (x-myu)
        es = x_[:,:,0] * x_[:,:,0] * self.covars[:,2]
        es += x_[:,:,1] * x_[:,:,1] * self.covars[:,0]
        es -= 2.0 * x_[:,:,0] * x_[:,:,1] * self.covars[:,1]
        es /= self._dets
        # calc 1/2 pi det(Sigma) exp
        es = np.exp(-0.5 * es)
        es /= self._divs

        ret = es @ weight # shape = (x_num,)

        if len(x_shape) == 0:
            ret = ret[0]
        else:
            ret = ret.reshape(x_shape)

        return ret
