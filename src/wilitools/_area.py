# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np

from ._floor import Floor
from ._gaussian import Gaussian
from ._rand import uniform_cube

class Area:
    """推定に必要なパラメータをまとめたクラス
    推定に必要なパラメータ5種（捜索範囲、初期動作確率、遷移確率、利用者位置分布、遷移失敗確率）をまとめたクラス

    Attributes
    ----------
    name : str | None
        name (optional)
    floor : Floor
        捜索範囲
    motion_num : int
        動作の数
    start_prob : numpy.ndarray
        初期動作確率を並べた1次元のnumpy配列
        （初期動作確率：各動作について利用者の最初の動作がその動作である確率）
    tr_prob : numpy.ndarray
        遷移確率を並べた2次元のnumpy配列
    gaussian : Gaussian
        各動作の利用者位置分布
    sample_size : int
        遷移失敗確率の分布は[0,1]^n上のサンプリング点と
        各点の密度関数の値で表される
        この変数はサンプリング点の個数
    miss_probs : numpy.ndarray
        サンプリング点を並べた2次元配列
        行数（1次元目の要素数）はsample_size
        列数（2次元目の要素数）はmotion_num
        i行j列目の要素はi番目のサンプリング点におけるj番目の動作の遷移失敗確率
    dens_miss_probs : numpy.ndarray
        サンプリング点の密度関数の値を並べた1次元のnumpy配列
        要素数はsample_size
        i番目の要素はi番目のサンプリング点における密度関数の値
    """
    def __init__(
        self, floor:Floor,
        start_prob:np.ndarray, tr_prob:np.ndarray, gaussian:Gaussian,
        miss_probs:np.ndarray, dens_miss_probs:np.ndarray,
        name:str=None
    ):
        # meta
        self.name = name
        self.floor = floor

        # hmm parameters
        self.motion_num = start_prob.shape[0]
        self.start_prob = start_prob
        self.tr_prob = tr_prob
        self.gaussian = gaussian

        # transition miss prob
        self.sample_size = dens_miss_probs.shape[0]
        self.miss_probs = miss_probs
        self.dens_miss_probs = dens_miss_probs # probability density of miss_probs


    def __str__(self) -> str:
        s_g = self.gaussian.__str__()
        s_t = self.tr_prob.__str__()

        h = '             '
        s = 'name       : %s\n' % self.name \
          + 'floor      : {}\n'.format(self.floor) \
          + 'motion_num : %d\n' % self.motion_num \
          + 'start_prob : {}\n'.format(self.start_prob) \
          + 'tr_prob    : ' + s_t.replace('\n', '\n' + h) + '\n' \
          + 'gaussian   : \n' + s_g + '\n' \
          + 'sample_num : %d' % self.sample_size
        return s


def create_default_area(floor:Floor, name:str = None, sample_num:int=300) -> Area:
    """デフォルト値のAreaインスタンスを作成
    デフォルト値のAreaインスタンスを作成
    捜索範囲だけは指定する必要がある

    Parameters
    ----------
    floor : Floor
        捜索範囲
    name : str, default None
        name (optional)
    sample_num : int, default 300
        遷移失敗確率の分布を表すサンプリング点の個数

    Returns
    -------
    default_area : Area
        デフォルト値のAreaインスタンス
    """
    # hmm parameters
    _a = floor.get_lattice(4)
    avrs = _a.reshape((_a.shape[0] * _a.shape[1], 2))

    n = avrs.shape[0]
    p = 1 / n

    init_prob = p * np.ones((n,), dtype=np.float32)
    tr_prob = p * np.ones((n, n), dtype=np.float32)
    covars = np.ones((n, 3), dtype=np.float32)
    covars[:,1] = np.zeros((n,), dtype=np.float32)

    # transition miss prob
    miss_probs = uniform_cube(n, sample_num)
    dens_miss_probs = np.ones((sample_num,), dtype=np.float32)

    return Area(
        floor,
        init_prob, tr_prob, Gaussian(avrs, covars),
        miss_probs, dens_miss_probs,
        name = name
    )
