# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import numpy as np
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from ._gaussian import Gaussian
from ._area import Area
from ._models import Base, AreaModel, MotionModel, InitProbModel, TrProbModel, SampleModel, MissProbModel

class wiliDB:
    def __init__(self, db_path:str):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)


    def create_area(self, area:Area) -> int:
        area_model = AreaModel()
        if (not area.name is None) and (len(area.name) > 1):
            area_model.name = area.name
        area_model.x_min = area.floor.x_min
        area_model.x_max = area.floor.x_max
        area_model.y_min = area.floor.y_min
        area_model.y_max = area.floor.y_max

        session = (sessionmaker(self.engine))()
        session.add(area_model)
        session.commit()
        area_id = area_model.id
        session.close()

        motion_ids = []
        for i in range(area.motion_num):
            motion_id = self.create_motion(area_id, area.gaussian.avrs[i], area.gaussian.covars[i])
            motion_ids.append(motion_id)

        self.create_init_prob(motion_ids, area.init_prob)
        self.create_tr_prob(motion_ids, area.tr_prob)
        self.create_samples(area_id, motion_ids, area.miss_probs, area.dens_miss_probs)

        return area_id


    def create_motion(self, area_id:int, avr:np.ndarray, covar:np.ndarray, name:str=None) -> int:
        motion_model = MotionModel()
        motion_model.area = area_id
        motion_model.avr_x = avr[0]
        motion_model.avr_y = avr[1]
        motion_model.covar_xx = covar[0]
        motion_model.covar_xy = covar[1]
        motion_model.covar_yy = covar[2]
        if not name is None:
            motion_model.name = name

        session = (sessionmaker(self.engine))()
        session.add(motion_model)
        session.commit()
        motion_id = motion_model.id
        session.close()

        return motion_id


    def create_init_prob(self, motion_ids:list[int], init_prob:np.ndarray):
        models = []
        for i in range(init_prob.shape[0]):
            init_prob_model = InitProbModel()
            init_prob_model.motion = motion_ids[i]
            init_prob_model.data = init_prob[i]
            models.append(init_prob_model)

        session = (sessionmaker(self.engine))()
        session.add_all(models)
        session.commit()
        session.close()


    def create_tr_prob(self, motion_ids:list[int], tr_prob:np.ndarray):
        n = tr_prob.shape[0]
        models = []
        for i in range(n):
            for j in range(n):
                tr_prob_model = TrProbModel()
                tr_prob_model.from_motion = motion_ids[i]
                tr_prob_model.to_motion = motion_ids[j]
                tr_prob_model.data = tr_prob[i, j]
                models.append(tr_prob_model)

        session = (sessionmaker(self.engine))()
        session.add_all(models)
        session.commit()
        session.close()


    def create_samples(self, area_id:int, motion_ids:list[int], miss_probs:np.ndarray, dens_miss_probs:np.ndarray):
        ns, nm = miss_probs.shape # ns=sample num, nm=motion num

        models = []
        for k in range(ns):
            sample_model = SampleModel()
            sample_model.area = area_id
            sample_model.dens = dens_miss_probs[k]
            models.append(sample_model)

        session = (sessionmaker(self.engine))()
        session.add_all(models)
        session.commit()

        sample_ids = [m.id for m in models]

        models = []
        for k in range(ns):
            for i in range(nm):
                miss_prob_model = MissProbModel()
                miss_prob_model.sample = sample_ids[k]
                miss_prob_model.motion = motion_ids[i]
                miss_prob_model.data = miss_probs[k, i]
                models.append(miss_prob_model)

        session = (sessionmaker(self.engine))()
        session.add_all(models)
        session.commit()
        session.close()


    def _select_init_prob(self, session:Session, area_id:int):
        return session.query(InitProbModel, MotionModel)\
            .outerjoin(MotionModel, InitProbModel.motion == MotionModel.id)\
            .filter(MotionModel.area == area_id)\
            .all()


    def _select_tr_prob(self, session:Session, area_id:int):
        return session.query(TrProbModel, MotionModel)\
            .outerjoin(MotionModel, TrProbModel.from_motion == MotionModel.id)\
            .filter(MotionModel.area == area_id)\
            .all()


    def _select_motions(self, session:Session, area_id:int):
        return session.query(MotionModel)\
            .filter(MotionModel.area == area_id)\
            .all()


    def _select_samples(self, session:Session, area_id:int):
        return session.query(SampleModel)\
            .filter(SampleModel.area == area_id)\
            .all()


    def _select_miss_probs(self, session:Session, area_id:int):
        return session.query(MissProbModel, SampleModel)\
            .outerjoin(SampleModel, MissProbModel.sample == SampleModel.id)\
            .filter(SampleModel.area == area_id)\
            .all()


    def read_init_prob(self, area_id:int) -> np.ndarray:
        session = (sessionmaker(self.engine))()
        query_res = self._select_init_prob(session, area_id)
        init_prob = [r[0].data for r in query_res]
        session.close()
        init_prob = np.array(init_prob, dtype=np.float32)
        return init_prob


    def read_tr_prob(self, area_id:int) -> np.ndarray:
        session = (sessionmaker(self.engine))()
        query_res = self._select_tr_prob(session, area_id)
        tr_prob = [r[0].data for r in query_res]
        session.close()
        tr_prob = np.array(tr_prob, dtype=np.float32)
        n = tr_prob.shape[0]
        n = int(np.round(np.sqrt(n)))
        tr_prob = tr_prob.reshape((n,n))
        return tr_prob


    def read_gaussian(self, area_id:int) -> Gaussian:
        session = (sessionmaker(self.engine))()
        query_res = self._select_motions(session, area_id)
        gaussian_arr = [[r.avr_x, r.avr_y, r.covar_xx, r.covar_xy, r.covar_yy] for r in query_res]
        session.close()
        gaussian_arr = np.array(gaussian_arr, dtype=np.float32)
        return Gaussian(gaussian_arr[:,[0,1]], gaussian_arr[:,[2,3,4]])


    def read_samples(self, area_id:int) -> tuple[np.ndarray, np.ndarray]:
        session = (sessionmaker(self.engine))()

        query_res = self._select_samples(session, area_id)
        densitys = [r.dens for r in query_res]
        densitys = np.array(densitys, dtype=np.float32)
        ns = densitys.shape[0]

        query_res = self._select_miss_probs(session, area_id)
        miss_probs = [r[0].data for r in query_res]
        session.close()
        miss_probs = np.array(miss_probs, dtype=np.float32)
        nm = int(np.round(miss_probs.shape[0] / ns))
        miss_probs = miss_probs.reshape((ns, nm))

        return (miss_probs, densitys)


    def update_init_prob(self, area_id:int, init_prob:np.ndarray):
        session = (sessionmaker(self.engine))()
        query_res = self._select_init_prob(session, area_id)
        for i, r in enumerate(query_res):
            r[0].data = init_prob[i]
        session.commit()
        session.close()


    def update_tr_prob(self, area_id:int, tr_prob:np.ndarray):
        tr_prob_flat = tr_prob.flatten()
        session = (sessionmaker(self.engine))()
        query_res = self._select_tr_prob(session, area_id)
        for i, r in enumerate(query_res):
            r[0].data = tr_prob_flat[i]
        session.commit()
        session.close()


    def update_gaussian(self, area_id:int, gaussian:Gaussian):
        session = (sessionmaker(self.engine))()
        query_res = self._select_motions(session, area_id)
        for i, r in enumerate(query_res):
            r.avr_x = gaussian.avrs[i, 0]
            r.avr_y = gaussian.avrs[i, 1]
            r.covar_xx = gaussian.covars[i, 0]
            r.covar_xy = gaussian.covars[i, 1]
            r.covar_yy = gaussian.covars[i, 2]
        session.commit()
        session.close()


    def update_samples(self, area_id:int, miss_probs:np.ndarray, dens_miss_probs:np.ndarray):
        session = (sessionmaker(self.engine))()

        query_res = self._select_samples(session, area_id)
        for i, r in enumerate(query_res):
            r.dens = dens_miss_probs[i]

        miss_probs_flat = miss_probs.flatten()
        query_res = self._select_miss_probs(session, area_id)
        for i, r in enumerate(query_res):
            r[0].data = miss_probs_flat[i]

        session.commit()
        session.close()


    def update_dens(self, area_id:int, dens_miss_probs:np.ndarray):
        session = (sessionmaker(self.engine))()

        query_res = self._select_samples(session, area_id)
        for i, r in enumerate(query_res):
            r.dens = dens_miss_probs[i]

        session.commit()
        session.close()


    def delete_area(self, area_id:int):
        session = (sessionmaker(self.engine))()
        area_model = session.get(AreaModel, area_id)
        session.delete(area_model)
        session.commit()
        session.close()
