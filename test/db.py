# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

#!/usr/bin/env python3

import os
import numpy as np
from wilitools import wiliDB, create_default_area, Floor

def test_db():
    db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")
    try:
        os.remove(db_path)
    except: pass
    db = wiliDB('sqlite:///{}'.format(db_path))

    area = create_default_area(Floor(-5.0, 5.0, -5.0, 5.0), sample_num=7)

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

    record = db.read_init_prob(area_id)
    assert record.shape == area.init_prob.shape
    assert np.allclose(record, area.init_prob)

    record = db.read_tr_prob(area_id)
    assert record.shape == area.tr_prob.shape
    assert np.allclose(record, area.tr_prob)

    record = db.read_gaussian(area_id)
    assert record.avrs.shape == area.gaussian.avrs.shape
    assert np.allclose(record.avrs, area.gaussian.avrs)
    assert record.covars.shape == area.gaussian.covars.shape
    assert np.allclose(record.covars, area.gaussian.covars)

    miss_probs, dens_miss_probs = db.read_samples(area_id)
    assert miss_probs.shape == area.miss_probs.shape
    assert np.allclose(miss_probs, area.miss_probs)
    assert dens_miss_probs.shape == area.dens_miss_probs.shape
    assert np.allclose(dens_miss_probs, area.dens_miss_probs)

    db.delete_area(area_id)
