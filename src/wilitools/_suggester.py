# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np
from numpy import ndarray

from ._gaussian import Gaussian
from ._rand import uniform_cube

class Suggester:
    def __init__(self,
        init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian,
        miss_probs:ndarray, dens_miss_probs:ndarray
    ):
        # ~~~ HMM ~~~
        # node
        self.motion_num = init_prob.shape[0]

        # initial motion probability
        self.init_prob = init_prob

        # transition probability
        self.tr_prob = tr_prob

        # Gaussian
        # average & covariance of position in each motion
        self.gaussian = gaussian

        # ~~~ transition miss probs ~~~
        # samples
        self.sample_num = dens_miss_probs.shape[0]
        self.miss_probs = miss_probs
        self.dens_miss_probs = dens_miss_probs # probability density of miss_probs


    def _weight(self, miss_prob:ndarray) -> ndarray:
        L = miss_prob.reshape((self.motion_num, 1)) * self.tr_prob.T
        L[np.diag_indices(self.motion_num)] = np.zeros(self.motion_num, dtype=np.float32)
        K = self.tr_prob.T - L
        return L @ np.linalg.inv(np.identity(self.motion_num, dtype=np.float32) - K) @ self.init_prob


    def _liklyhood(self, x:ndarray, miss_prob:ndarray) -> float:
        return self.gaussian.weighted(x, self._weight(miss_prob))


    def _expectation(self, f) -> float | ndarray:
        sum_f = self.dens_miss_probs[0] * f(self.miss_probs[0,:])
        for i in range(1, self.sample_num):
            sum_f += self.dens_miss_probs[i] * f(self.miss_probs[i,:])
        return sum_f / self.sample_num


    def update(self, where_found:ndarray) -> None:
        # ---memo-------
        # p : lost item probability, _weight
        # b : position distribution of motion
        # E[pb] = E[p]b
        # --------------
        exp_l = self.suggest(where_found)
        for i in range(self.sample_num):
            self.dens_miss_probs[i] = self._liklyhood(where_found, self.miss_probs[i,:]) * self.dens_miss_probs[i]
        self.dens_miss_probs /= exp_l


    def suggest(self, x:ndarray) -> float | ndarray:
        return self.gaussian.weighted(x, self._expectation(self._weight))
