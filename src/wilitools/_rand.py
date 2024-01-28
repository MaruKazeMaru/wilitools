# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np

def uniform_simplex(dim:int, size:int=None) -> np.ndarray:
    if size is None:
        v = np.random.exponential(scale=1, size=dim).astype(np.float32)
        return v / np.sum(v)
    else:
       v = np.random.exponential(scale=1, size=dim * size).astype(np.float32).reshape((dim, size))
       return (v / np.sum(v, axis=0)).T


def uniform_cube(dim:int, size:int=None) -> np.ndarray:
    if size is None:
        v = np.random.uniform(0, 1, dim).astype(np.float32)
        return v
    else:
       v = np.random.uniform(0, 1, dim * size).astype(np.float32).reshape((size, dim))
       return v
