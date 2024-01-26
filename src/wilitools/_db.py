# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ._gaussian import Gaussian
from ._area import Area
from wilitools._models import Base, AreaModel, MotionModel, InitProbModel, TrProbModel, SampleModel, MissProbModel

class wiliDB:
    def __init__(self, db_path:str):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)


    def create_area(self, area:Area) -> int:
        session = (sessionmaker(self.engine))()
        area_model = AreaModel()
        if (not area.name is None) and (len(area.name) > 1):
            area_model.name = area.name
        area_model.x_min = area.floor.xmin
        area_model.x_max = area.floor.xmax
        area_model.y_min = area.floor.ymin
        area_model.y_max = area.floor.ymax
        session.add(area_model)
        session.commit()
        area_id = area_model.id
        session.close()

        for i in range(area.motion_num):
            self.create_motion(area_id, area.gaussian.avrs[i], area.gaussian.covars[i])

        return area_id


    def create_motion(self, area_id:int, avr:np.ndarray, covar:np.ndarray):
        session = (sessionmaker(self.engine))()
        motion_model = MotionModel()
        motion_model.area = area_id
        motion_model.avr_x = avr[0]
        motion_model.avr_y = avr[1]
        motion_model.covar_xx = covar[0]
        motion_model.covar_xy = covar[1]
        motion_model.covar_yy = covar[2]
        session.add(motion_model)
        session.commit()
        session.close()


    def create_init_prob(self, area_id:int): pass


    def read_init_prob(self, area_id:int) -> np.ndarray:
        session = (sessionmaker(self.engine))()
        query_res = session.query(InitProbModel, MotionModel)\
            .outerjoin(MotionModel, InitProbModel.motion == MotionModel.id)\
            .filter(MotionModel.area == area_id)\
            .all()
        init_prob_list = [r.tuple()[0].data for r in query_res]
        session.close()
        return np.array(init_prob_list)


    def read_tr_prob(self, area_id:int) -> np.ndarray: pass


    def read_gaussian(self, area_id:int) -> Gaussian:
        session = (sessionmaker(self.engine))()
        query_res = session.query(MotionModel)\
            .filter(MotionModel.area == area_id)\
            .all()
        gaussian_arr = [[r.avr_x, r.avr_y, r.covar_xx, r.covar_xy, r.covar_yy] for r in query_res]
        session.close()
        gaussian_arr = np.array(gaussian_arr)
        return Gaussian(gaussian_arr[:,[0,1]], gaussian_arr[:,[2,3,4]])


    def read_samples(self, area_id:int) -> tuple[np.ndarray, np.ndarray]: pass
