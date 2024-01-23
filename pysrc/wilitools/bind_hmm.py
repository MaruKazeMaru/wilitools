# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import ctypes as c
import os

import numpy as np
from numpy import ndarray

from . import Gaussian

class _hmm_t(c.Structure):
    _fields_ = [
        ("motion_num", c.c_ulong),
        ("tr_prob", c.POINTER(c.POINTER(c.c_double))),
        ("avrs", c.POINTER(c.POINTER(c.c_double))),
        ("covars", c.POINTER(c.POINTER(c.c_double)))
    ]

# c.POINTER(c.POINTER(c.c_double)) を吐くように直せ
def ndarray2cptr(arr:ndarray):
    arr_f = arr.flatten()
    n = arr_f.shape[0]
    p = (c.c_double * n)()
    p[:] = arr_f.tolist()
    return c.cast(p, c.POINTER(c.c_double))


def cptrptr2ndarray(row:int, col:int, pp):
    arr = ndarray((row, col), dtype=np.double)
    for i in range(row):
        for j in range(col):
            arr[i,j] = pp[i][j]
    return arr


class HMM:
    def __init__(self, tr_prob:ndarray, gaussian:Gaussian):
        self.tr_prob = tr_prob
        self.gaussian = gaussian


    def _get_libhmm_and_chmm(self):
        c_obj_dir = os.path.join(os.path.dirname(__file__), "..", "cbuild", "obj")
        libhmm_path = os.path.join(c_obj_dir, "libhmm.so")

        libhmm = c.cdll.LoadLibrary(libhmm_path)

        libhmm.construct_hmm.argtypes = (
            c.c_ulong,
            c.POINTER(c.c_double),
            c.POINTER(c.c_double),
            c.POINTER(c.c_double)
        )
        libhmm.construct_hmm.restype = c.POINTER(_hmm_t)

        libhmm.destroy_hmm.argtypes = (c.POINTER(_hmm_t),)
        libhmm.destroy_hmm.restype = None

        chmm = libhmm.construct_hmm(
            c.c_ulong(self.tr_prob.shape[0]),
            ndarray2cptr(self.tr_prob),
            ndarray2cptr(self.gaussian.avrs),
            ndarray2cptr(self.gaussian.covars)
        )

        return libhmm, chmm


    def baum_welch(self, observation:ndarray):
        n = self.tr_prob.shape[0]
        t = observation.shape[0]

        libhmm, chmm = self._get_libhmm_and_chmm()

        libhmm.baum_welch.argtypes = (
            c.POINTER(_hmm_t),
            c.POINTER(c.c_double)
        )
        libhmm.baum_welch.restype = None
        libhmm.baum_welch(chmm, ndarray2cptr(observation))

        self.tr_prob = cptrptr2ndarray(n, n, chmm[0].tr_prob)
        self.gaussian.avrs = cptrptr2ndarray(n, 2, chmm[0].avrs)
        self.gaussian.covars = cptrptr2ndarray(n, 3, chmm[0].covars)

        libhmm.destroy_hmm(chmm)
