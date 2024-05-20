# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import json

import numpy as np

from ._area import Area
from ._floor import Floor
from ._gaussian import Gaussian
from ._rand import uniform_cube
from ._suggester import Suggester


def _dict_to_area(data:dict) -> Area:
    kwargs = {}

    if 'name' in data:
        kwargs['name'] = data['name']
    floor = Floor(
        float(data['x_min']), float(data['x_max']),
        float(data['y_min']), float(data['y_max'])
    )

    start_prob = np.array(data['start_prob'], dtype=np.float32)
    tr_prob = np.array(data['tr_prob'], dtype=np.float32)
    avrs = np.array(data['avrs'], dtype=np.float32)
    covars = np.array(data['covars'], dtype=np.float32)
    gaussian = Gaussian(avrs, covars)

    if ('miss_probs' in data) and ('dens_miss_probs' in data):
        miss_probs = np.array(data['miss_probs'], dtype=np.float32)
        miss_probs = np.array(data['dens_miss_probs'], dtype=np.float32)
    else:
        if 'sample_num' in data:
            sample_num = int(data['sample_num'])
        else:
            sample_num = 300
        motion_num = start_prob.shape[0]
        miss_probs = uniform_cube(motion_num, size=sample_num)
        dens_miss_probs = np.ones(sample_num, dtype=np.float32)

    return Area(
        floor,
        start_prob, tr_prob, gaussian,
        miss_probs, dens_miss_probs,
        **kwargs
    )


def _area_to_dict(area:Area, miss_probs_in:bool=False):
    data = {}
    if area.name:
        data['name'] = area.name
    data['motion_num'] = area.motion_num
    data['start_prob'] = area.start_prob.tolist()
    data['tr_prob'] = area.tr_prob.tolist()
    data['avrs']   = area.gaussian.avrs.tolist()
    data['covars'] = area.gaussian.covars.tolist()

    data['sample_num'] = area.sample_size
    if miss_probs_in:
        data['miss_probs'] = area.miss_probs.tolist()
        data['dens_miss_probs'] = area.dens_miss_probs.tolist()

    return data


def json_to_area(json_path:str) -> Area:
    with open(json_path) as f:
        data = json.load(f)
    return _dict_to_area(data)


def area_to_json(json_path:str, area:Area, miss_probs_in:bool=False, json_dump_kwargs:dict={}):
    with open(json_path, mode='w') as f:
        data = _area_to_dict(area, miss_probs_in=miss_probs_in)
        json.dump(data, f, **json_dump_kwargs)


def area_to_suggester(area:Area) -> Suggester:
    return Suggester(
        area.start_prob, area.tr_prob, area.gaussian,
        area.miss_probs, area.dens_miss_probs
    )
