# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import numpy as np
from wilitools import create_default_area, area_to_suggester, Floor

def test_suggester():
    area = create_default_area(Floor(-5.0, 5.0, -5.0, 5.0), sample_num=10)
    suggester = area_to_suggester(area)
    lattice = area.floor.get_lattice(2.0)
    suggester.suggest(lattice)
    suggester.update(np.ones(2))
    suggester.suggest(lattice)
