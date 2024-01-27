# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import numpy as np
from wilitools import Gaussian

def main():
    gaussian = Gaussian(
        np.array([[0.0, 1.1],       [-0.5, 0.1]]),
        np.array([[1.2, -0.3, 0.8], [0.7, 0.2, 0.3]])
    )
    weight = np.array([0.6, 0.4])
    gaussian.weighted(np.random.random((2,)), weight)
    gaussian.weighted(np.random.random((2,2)), weight)
    gaussian.weighted(np.random.random((2,2,2)), weight)
    print(gaussian)


if __name__ == "__main__":
    main()
