# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

class NegativeFloor(Exception):
    def __init__(self, x_min:float, x_max:float, y_min:float, y_max:float) -> None:
        messages = []
        if x_min > x_max:
            messages.append('x_min > x_max ( x_min={}, x_max={})'.format(x_min, x_max))
        if y_min > y_max:
            messages.append('y_min > y_max ( y_min={}, y_max={})'.format(y_min, y_max))
        super().__init__(', '.join(messages))
