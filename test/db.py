# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import os
from wilitools import wiliDB, create_default_area, Floor

def main():
    db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
    try:
        os.remove(db_path)
    except: pass
    db = wiliDB('sqlite:///{}'.format(db_path))

    area = create_default_area(Floor(-5.0, 5.0, -5.0, 5.0))

    area_id = db.create_area(area)

    area.init_prob[0] = 0
    area.tr_prob[0,0] = 0
    area.gaussian.avrs[0,0] = 0
    area.gaussian.covars[0,0] = 0
    area.miss_probs[0,0] = 0
    area.dens_miss_probs[0] = 0

    db.update_init_prob(area_id, area.init_prob)
    db.update_tr_prob(area_id, area.tr_prob)
    db.update_gaussian(area_id, area.gaussian)
    db.update_samples(area_id, area.miss_probs, area.dens_miss_probs)

    print(db.read_init_prob(area_id))
    print(db.read_gaussian(area_id))
    print(db.read_tr_prob(area_id))
    miss_probs, densitys = db.read_samples(area_id)
    print(miss_probs)
    print(densitys)

    db.delete_area(area_id)


if __name__ == "__main__":
    main()
