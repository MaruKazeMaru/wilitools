import os

from db import WiliDB
from area import Area, json_to_area, area_to_json

if __name__ == '__main__':
    db_path = 'test/data/db'
    if os.path.exists(db_path):
        os.remove(db_path)
    db = WiliDB(db_path)
    area_i = json_to_area('test/data/i.json')
    db.initialize_area(area_i)
    area_id = db.get_area_id(area_i.name)
    area_o = Area(
        area_i.name,
        db.get_init_prob_all(area_id),
        db.get_tr_prob_mat(area_id),
        db.get_gaussian_all(area_id)
    )
    area_to_json('test/data/o.json', area_o)
