import numpy as np
from numpy import ndarray

from .gaussian import Gaussian
from .rand import uniform_cube

class Suggester:
    def __init__(self,
        init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian,
        sample:ndarray, dens_sample:ndarray
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

        # sample
        self.sample_num = dens_sample.shape[0]
        self.sample = sample
        self.dens_sample = dens_sample


    def weight(self, miss_prob:ndarray) -> ndarray:
        L = miss_prob.reshape((self.motion_num, 1)) * self.tr_prob.T
        L[np.diag_indices(self.motion_num)] = np.zeros(self.motion_num)
        K = self.tr_prob.T - L
        return L @ np.linalg.inv(np.identity(self.motion_num) - K) @ self.init_prob


    # def gaussian(self, x:ndarray) -> ndarray:
    #     e = ndarray((self.motion_num,))
    #     x_s = x - self.avrs
    #     for i in range(self.motion_num):
    #         e[i] = x_s[i] @ self.inv_covars[i] @ x_s[i]
    #         e[i] = np.exp(-0.5 * e[i])
    #         e[i] /= self.gauss_divs[i]
    #     return e


    def liklyhood(self, miss_prob:ndarray, x:ndarray=None) -> float:
        return self.gaussian.weighted(x, self.weight(miss_prob))


    def expectation(self, f, f_kwargs:dict={}) -> float | ndarray:
        sum_f = 0.0
        for i in range(self.sample_num):
            sum_f += self.dens_sample[i] * f(self.sample[i,:])
        return sum_f / self.sample_num


    def update(self, where_found:ndarray) -> None:
        exp_l = self.gaussian.weighted(where_found, self.expectation(self.weight))
        for i in range(self.sample_num):
            self.dens_sample[i] = self.liklyhood(self.sample[i,:], x=where_found) * self.dens_sample[i]
        self.dens_sample /= exp_l


    def suggest(self) -> ndarray:
        return self.expectation(self.weight)
