# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools import Floor

def test_floor():
    try:
        Floor(1.0, 0.0, 0.0, 3.0)
    except ValueError:
        pass
    else:
        raise Exception('NegativeFloor was not raised')

    f = Floor(-6.0, 6.0, -5.0, 5.0)
    lattice = f.get_lattice(4.0)
    assert lattice.shape == (3, 2, 2)
    str(f)
