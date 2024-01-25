import ctypes as c
import os

import numpy as np
from numpy import ndarray

from . import Gaussian

class _hmm_t(c.Structure):
    _fields_ = [
        ("motion_num", c.c_uint8),
        ("init_prob", c.POINTER(c.c_double)),
        ("tr_prob", c.POINTER(c.POINTER(c.c_double))),
        ("avrs", c.POINTER(c.POINTER(c.c_double))),
        ("covars", c.POINTER(c.POINTER(c.c_double)))
    ]


def _np2c(arr:ndarray):
    shape = list(arr.shape)

    #create instance
    ret_type = c.c_double
    for n in reversed(shape):
        ret_type = ret_type * n
    ret = (ret_type)()

    # set values
    _recurs_np2c(shape, arr, ret)

    # cast array -> pointer
    ret_type = c.c_double
    for _ in shape:
        ret_type = c.POINTER(ret_type)
    ret = c.cast(ret, ret_type)

    return ret


def _recurs_np2c(shape:list[int], arr:ndarray, ptr):
    if len(shape) == 1:
        ptr[:] = arr.tolist()
    else:
        for i in range(shape[0]):
            _recurs_np2c(shape[1:], arr[i], ptr[i])


def _c2np(shape:list[int], ptr):
    # create_instance
    ret = np.ndarray(shape, dtype=np.double)
    # set values
    _recurs_c2np(shape, ptr, ret)
    print(ret)
    return ret


def _recurs_c2np(shape:list[int], ptr, arr:ndarray):
    if len(shape) == 1:
        arr = np.array(ptr[:shape[0]])
    else:
        for i in range(shape[0]):
            _recurs_c2np(shape[1:], ptr[i], arr[i])


def _np2c_mat(arr:ndarray):
    nr = arr.shape[0]
    nc = arr.shape[1]
    ptr = ((c.c_double * nc) * nr)()
    for i in range(nr):
        for j in range(nc):
            ptr[i][j] = arr[i][j]
    return c.cast(ptr, c.POINTER(c.POINTER(c.c_double)))


def _np2c_vec(arr:ndarray):
    n = arr.shape[0]
    ptr = (c.c_double * n)()
    for i in range(n):
        ptr[i] = arr[i]
    return c.cast(ptr, c.POINTER(c.c_double))


def _c2np_mat(nr:int, nc:int, ptr):
    arr = np.ndarray((nr, nc), dtype=np.double)
    for i in range(nr):
        for j in range(nc):
            arr[i][j] = ptr[i][j]
    return arr


def _c2np_vec(n:int, ptr):
    arr = np.ndarray((n,), dtype=np.double)
    for i in range(n):
        arr[i] = ptr[i]
    return arr


class HMM:
    def __init__(self, init_prob:ndarray, tr_prob:ndarray, gaussian:Gaussian):
        self.init_prob = init_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian


    def _get_libhmm_and_chmm(self):
        c_obj_dir = os.path.join(os.path.dirname(__file__), "cbuild", "obj")
        libhmm_path = os.path.join(c_obj_dir, "libwilihmm.so")

        libhmm = c.cdll.LoadLibrary(libhmm_path)

        libhmm.construct_hmm.argtypes = (
            c.c_uint8,
            c.POINTER(c.c_double),
            c.POINTER(c.POINTER(c.c_double)),
            c.POINTER(c.POINTER(c.c_double)),
            c.POINTER(c.POINTER(c.c_double))
        )
        libhmm.construct_hmm.restype = c.POINTER(_hmm_t)

        libhmm.destroy_hmm.argtypes = (c.POINTER(_hmm_t),)
        libhmm.destroy_hmm.restype = None

        chmm = libhmm.construct_hmm(
            c.c_uint8(self.tr_prob.shape[0]),
            _np2c_vec(self.init_prob),
            _np2c_mat(self.tr_prob),
            _np2c_mat(self.gaussian.avrs),
            _np2c_mat(self.gaussian.covars)
        )

        return libhmm, chmm


    def baum_welch(self, observation:ndarray):
        n = self.tr_prob.shape[0]
        t = observation.shape[0]

        libhmm, chmm = self._get_libhmm_and_chmm()

        libhmm.baum_welch.argtypes = (
            c.POINTER(_hmm_t),
            c.c_uint,
            c.POINTER(c.POINTER(c.c_double))
        )
        libhmm.baum_welch.restype = None
        libhmm.baum_welch(chmm, c.c_uint(observation.shape[0]), _np2c_mat(observation))

        self.init_prob = _c2np_vec(n, chmm[0].init_prob)
        self.tr_prob = _c2np_mat(n, n, chmm[0].tr_prob)
        self.gaussian.avrs = _c2np_mat(n, 2, chmm[0].avrs)
        self.gaussian.covars = _c2np_mat(n, 3, chmm[0].covars)

        libhmm.destroy_hmm(chmm)
