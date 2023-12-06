from numpy import ndarray

class Gaussian:
    def __init__(self, avrs:ndarray, covars:ndarray):
        self.avrs = avrs
        self.covars = covars


    # def weighted(self, x:ndarray, weight:ndarray) -> ndarray:
    #     x_ = x
    #     if len(x.shape) == 0:
    #         x_ = x.reshape((1,2))

    #     e = 
