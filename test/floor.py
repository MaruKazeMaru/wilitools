# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools import Floor, NegativeFloor

def test_floor():
    try:
        Floor(1.0, 0.0, 0.0, 3.0)
    except NegativeFloor:
        pass
    else:
        raise Exception('NegativeFloor was not raised')

    f = Floor(-6.0, 6.0, -5.0, 5.0)
    lattice = f.lattice_from_delta(4.0)
    assert lattice.shape == (3, 2, 2)
    str(f)
