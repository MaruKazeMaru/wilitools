import numpy as np
from numpy import ndarray

from .gaussian import Gaussian


class Suggester:
    def __init__(self, init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian):
        self.init_prob = init_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian


    # def _weight(self) -> ndarray:
    #     pass


    # def suggest(self, area_rect:tuple[float, float, float, float], resolution:tuple[int, int]) -> ndarray:
    #     w = self._weight()
    #     x_step = 
    #     x = np.arange(, dtype='float32')
    #     np.meshgrid()
