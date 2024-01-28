# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

from wilitools import NegativeFloor

def test_exceptions():
    NegativeFloor(0.0, -1.0, 0.0, 1.0)
