from numpy import ndarray
from .gaussian import Gaussian

class Area:
    def __init__(self, name:str, init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian):
        self.name = name
        self.motion_num = init_prob.shape[0]
        self.init_prob = init_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian