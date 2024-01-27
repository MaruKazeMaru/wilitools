# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools import create_default_area, Floor

def test_area():
    area = create_default_area(Floor(-5.0, 5.0, -5.0, 5.0))
    str(area)
