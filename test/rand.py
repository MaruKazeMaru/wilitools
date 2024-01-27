# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools._rand import uniform_simplex, uniform_cube

def main():
    uniform_simplex(2)
    uniform_simplex(2, size=2)
    uniform_cube(2)
    uniform_cube(2, size=2)


if __name__ == "__main__":
    main()
