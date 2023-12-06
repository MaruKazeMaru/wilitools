import json

import numpy as np

from .gaussian import Gaussian
from .area import Area


def json_to_area(json_path:str) -> Area:
    with open(json_path) as f:
        data = json.load(f)
        try:
            name = data['name']
        except IndexError:
            name = None
        init_prob = np.array(data['init_prob'], dtype='float32')
        tr_prob = np.array(data['tr_prob'], dtype='float32')
        avrs = []
        covars = []
        for g in data['gaussian']:
            avrs.append(g['avr'])
            covars.append(g['covar'])
        gaussian = Gaussian(
            np.array(avrs, dtype='float32'),
            np.array(covars, dtype='float32')
        )
        area = Area(name, init_prob, tr_prob, gaussian)
    
    return area


def area_to_json(json_path:str, area:Area):
    data = {}
    data['name'] = area.name
    data['motion_num'] = area.motion_num
    data['init_prob'] = area.init_prob.tolist()
    data['tr_prob'] = area.tr_prob.tolist()
    data['gaussian'] = []
    for i in range(area.motion_num):
        data['gaussian'].append({
            'avr': area.gaussian.avrs[i].tolist(),
            'covar': area.gaussian.covars[i].tolist(),
        })

    with open(json_path, mode='w') as f:
        json.dump(data, f)

    return
