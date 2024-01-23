# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import json

import numpy as np

from .area import Area
from .floor import Floor
from .gaussian import Gaussian
from .rand import uniform_cube
from .suggester import Suggester


def dict_to_area(data:dict) -> Area:
    name = data['name']
    floor = Floor(
        float(data['xmin']), float(data['xmax']),
        float(data['ymin']), float(data['ymax'])
    )

    motion_num = int(data['motion_num'])
    sample_num = int(data['sample_num'])

    init_prob = np.array(data['init_prob'], dtype=np.float32).reshape(motion_num)
    tr_prob = np.array(data['tr_prob'], dtype=np.float32).reshape(motion_num, motion_num)
    avrs = np.array(data['avrs'], dtype=np.float32).reshape(motion_num, 2)
    covars = np.array(data['covars'], dtype=np.float32).reshape(motion_num, 3)
    gaussian = Gaussian(avrs, covars)

    samples = uniform_cube(motion_num, sample_num)
    dens_samples = np.ones(sample_num, dtype=np.float32)

    return Area(
        name, floor,
        init_prob, tr_prob, gaussian,
        samples, dens_samples
    )


def json_to_area(json_path:str) -> Area:
    with open(json_path) as f:
        data = json.load(f)
    return dict_to_area(data)


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


def area_to_suggester(area:Area) -> Suggester:
    return Suggester(
        area.init_prob, area.tr_prob,
        area.gaussian.avrs, area.gaussian.covars,
        area.sample, area.dens_sample
    )