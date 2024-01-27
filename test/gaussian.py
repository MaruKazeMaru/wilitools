# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import numpy as np
from wilitools import Gaussian

def test_gaussian():
    gaussian = Gaussian(
        np.array([[0.0, 1.1],       [-0.5, 0.1]]),
        np.array([[1.2, -0.3, 0.8], [0.7, 0.2, 0.3]])
    )

    weight = np.array([0.6, 0.4])

    gx = gaussian.weighted(np.random.random((2,)), weight)
    assert type(gx) == np.float32
    gx = gaussian.weighted(np.random.random((3,2)), weight)
    assert gx.shape == (3,)
    gx = gaussian.weighted(np.random.random((4,3,2)), weight)
    assert gx.shape == (4,3)

    str(gaussian)
