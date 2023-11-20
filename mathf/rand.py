import numpy as np
from numpy import ndarray

def uniform_simplex(dim:int, size:int=None) -> ndarray:
    if size is None:
        v = np.random.exponential(scale=1, size=dim)
        return v / np.sum(v)
    else:
       v = np.random.exponential(scale=1, size=dim * size).reshape((dim, size))
       return (v / np.sum(v, axis=0)).T
