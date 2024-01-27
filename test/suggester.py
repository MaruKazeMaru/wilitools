# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import numpy as np
from wilitools import create_default_area, area_to_suggester, Floor

def main():
    area = create_default_area(Floor(-5.0, 5.0, -5.0, 5.0))
    suggester = area_to_suggester(area)
    lattice = area.floor.lattice_from_delta(2.0)
    print(suggester.suggest(lattice))
    suggester.update(np.ones(2, dtype=np.float32))
    print(suggester.suggest(lattice))


if __name__ == "__main__":
    main()
