# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

class UnexistRecord(Exception):
    def __init__(self, table:str, columns:list[str]=[], values:list=[]):
        wheres = []
        for c, v in zip(columns, values):
            wheres.append("{}={}".format(c, v))
        super().__init__("table " + table + " has no record where " + ", ".join(wheres))

class NegativeFloor(Exception):
    def __init__(self, xmin:float, xmax:float, ymin:float, ymax:float) -> None:
        messages = []
        if xmin > xmax:
            messages.append('xmin > xmax ( xmin={}, xmax={})'.format(xmin, xmax))
        if ymin > ymax:
            messages.append('ymin > ymax ( ymin={}, ymax={})'.format(ymin, ymax))
        super().__init__(', '.join(messages))
