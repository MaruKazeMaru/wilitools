# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools._rand import uniform_simplex, uniform_cube

def test_rand():
    r = uniform_simplex(2)
    assert r.shape == (2,)
    r = uniform_simplex(2, size=3)
    assert r.shape == (3,2)
    r = uniform_cube(2)
    assert r.shape == (2,)
    r = uniform_cube(2, size=3)
    assert r.shape == (3,2)
