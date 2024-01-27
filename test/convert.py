# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import os
from wilitools import json_to_area, area_to_json, area_to_suggester

def main():
    json_path = os.path.join(os.path.dirname(__file__), "area_in.json")
    area = json_to_area(json_path)
    suggester = area_to_suggester(area)
    json_path = os.path.join(os.path.dirname(__file__), "area_out.json")
    area_to_json(json_path, area, json_dump_kwargs={'indent': 2})


if __name__ == "__main__":
    main()
