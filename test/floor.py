# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools import Floor, NegativeFloor

def main():
    try:
        Floor(1.0, 0.0, 0.0, 3.0)
    except NegativeFloor:
        pass

    f = Floor(-5.0, 5.0, -5.0, 5.0)
    f.lattice_from_delta(4.0)
    print(f)


if __name__ == "__main__":
    main()
