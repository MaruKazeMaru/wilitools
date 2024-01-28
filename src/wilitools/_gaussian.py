# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

from __future__ import annotations
import numpy as np

class Gaussian:
    def __init__(self, avrs:np.ndarray, covars:np.ndarray):
        # validate
        if len(avrs.shape) != 2:
            raise ValueError('avrs is not 2d array. its shape is {}'.format(avrs.shape))
        if avrs.shape[1] != 2:
            raise ValueError('avrs.shape[1] != 2. avrs.shape={}'.format(avrs.shape))
        if len(covars.shape) != 2:
            raise ValueError('covars is not 2d array. its shape is {}'.format(covars.shape))
        if covars.shape[1] != 3:
            raise ValueError('covars.shape[1] != 2. covars.shape={}'.format(covars.shape))
        if avrs.shape[0] != covars.shape[0]:
            raise ValueError('unmatch shape[0] between avrs and covars. avrs.shape={}, covars.shape={}'.format(avrs.shape, covars.shape))

        self.avrs = avrs.astype(np.float32)
        self.covars = covars.astype(np.float32)

        # cache
        self._dets:np.ndarray = None
        self._divs:np.ndarray = None


    def __str__(self) -> str:
        s_a = self.avrs.__str__()
        s_c = self.covars.__str__()
        h = '         '
        s = 'avrs   : ' + s_a.__str__().replace('\n', '\n' + h) + '\n' \
          + 'covars : ' + s_c.__str__().replace('\n', '\n' + h)
        return s


    def weighted(self, x:np.ndarray, weight:np.ndarray) -> np.float32 | np.ndarray:
        if self._divs is None:
            self._dets = self.covars[:,0] * self.covars[:,2] - self.covars[:,1] * self.covars[:,1]
            self._divs = 2.0 * np.pi * self._dets

        x_num = 1
        x_shape = [n for n in x.shape]
        x_shape = x_shape[:-1]
        for n in x_shape:
            x_num *= n

        motion_num = self.avrs.shape[0]

        x_ = x.astype(np.float32).reshape((x_num, 1, 2)) - self.avrs.reshape((1, motion_num, 2))
        # calc (x-myu)^T Sigma^-1 (x-myu)
        es = x_[:,:,0] * x_[:,:,0] * self.covars[:,2]
        es += x_[:,:,1] * x_[:,:,1] * self.covars[:,0]
        es -= 2.0 * x_[:,:,0] * x_[:,:,1] * self.covars[:,1]
        es /= self._dets
        # calc 1/2 pi det(Sigma) exp
        es = np.exp(-0.5 * es)
        es /= self._divs

        ret = es @ weight.astype(np.float32) # shape = (x_num,)

        if len(x_shape) == 0:
            ret = ret[0]
        else:
            ret = ret.reshape(x_shape)

        return ret
