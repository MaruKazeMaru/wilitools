# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools import create_default_area, Floor

def main():
    area = create_default_area(Floor(-5.0, 5.0, -5.0, 5.0))
    print(area)


if __name__ == "__main__":
    main()
