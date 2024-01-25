# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

import os
import datetime
import sqlite3

import numpy as np
from numpy import ndarray

from ._area import Area
from ._exceptions import UnexistRecord
from ._floor import Floor
from ._gaussian import Gaussian

class WiliDB:
    def __init__(self, db_path:str):
        already_exist = os.path.exists(db_path)
        if not already_exist:
            f = open(db_path, 'wb')
            f.close()
        self._con = sqlite3.connect(db_path)
        self._cur = self._con.cursor()
        if not already_exist:
            self._create_tables()


    def __del__(self):
        self._con.close()


    def _create_tables(self):
        # CREATE TABLES
        self._cur.execute("PRAGMA foreign_keys=true")

        # meta
        self._cur.execute(
            "CREATE TABLE area(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "name TEXT," \
            "xmin REAL,xmax REAL," \
            "ymin REAL,ymax REAL," \
            "UNIQUE(name)" \
            ")"
        )
        self._cur.execute(
            "CREATE TABLE history(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "area INTEGER," \
            "time DATETIME," \
            "comment TEXT," \
            "FOREIGN KEY(area) REFERENCES area(id)" \
            ")"
        )

        self._cur.execute(
            "CREATE TABLE motion(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "name TEXT," \
            "area INTEGER," \
            "FOREIGN KEY(area) REFERENCES area(id)" \
            ")"
        )

        # hmm parameters
        self._cur.execute(
            "CREATE TABLE init_prob(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "motion INTEGER," \
            "data REAL," \
            "FOREIGN KEY(motion) REFERENCES motion(id)," \
            "UNIQUE(motion)" \
            ")"
        )
        self._cur.execute(
            "CREATE TABLE tr_prob(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "from_motion INTEGER," \
            "to_motion INTEGER," \
            "data REAL," \
            "FOREIGN KEY(from_motion) REFERENCES motion(id)," \
            "FOREIGN KEY(to_motion) REFERENCES motion(id)," \
            "UNIQUE(from_motion, to_motion)" \
            ")"
        )
        self._cur.execute(
            "CREATE TABLE gaussian(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "motion INTEGER," \
            "avr_x REAL," \
            "avr_y REAL," \
            "covar_xx REAL," \
            "covar_xy REAL," \
            "covar_yy REAL," \
            "FOREIGN KEY(motion) REFERENCES motion(id)," \
            "UNIQUE(motion)" \
            ")"
        )

        # transition failure prob
        self._cur.execute(
            "CREATE TABLE sample(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "dens REAL," \
            "area INTEGER," \
            "FOREIGN KEY(area) REFERENCES area(id)" \
            ")"
        )
        self._cur.execute(
            "CREATE TABLE sample_elem(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "sample INTEGER," \
            "motion INTEGER," \
            "data REAL," \
            "FOREIGN KEY(sample) REFERENCES sample(id)," \
            "FOREIGN KEY(motion) REFERENCES motion(id)," \
            "UNIQUE(sample,motion)" \
            ")"
        )

        self._con.commit()


    def insert_area(self, area:Area) -> int:
        self._cur.execute(
            "INSERT INTO area(name, xmin, xmax, ymin, ymax)" \
            " VALUES ('%s',%f,%f,%f,%f)" \
            % (area.name, area.floor.xmin, area.floor.xmax, area.floor.ymin, area.floor.ymax)
        )
        self._con.commit()

        aid = self.get_area_id(area.name)

        # INSERT INTO motion
        values = ["(%d)" % aid] * area.motion_num
        self._cur.execute("INSERT INTO motion(area) VALUES " + ",".join(values))
        self._con.commit()
        motion_ids = self.get_motion_ids(aid)

        # INSERT INTO sample
        values = []
        for d in area.dens_sample.tolist():
            values.append("({},{})".format(d, aid))
        self._cur.execute(
            "INSERT INTO sample(dens, area) VALUES"
            + ",".join(values)
        )
        self._con.commit()
        sample_ids = self.get_sample_ids(aid)

        # INSERT INTO init_prob
        values = []
        for i, mid in enumerate(motion_ids):
            values.append("(%d,%f)" % (mid, area.init_prob[i]))
        self._cur.execute(
            "INSERT INTO init_prob(motion, data) VALUES "
            + ",".join(values)
        )

        # INSERT INTO tr_prob
        values = []
        for i1, mid1 in enumerate(motion_ids):
            for i2, mid2 in enumerate(motion_ids):
                values.append("(%d,%d,%f)" % (mid1, mid2, area.tr_prob[i1,i2]))
        self._cur.execute(
            "INSERT INTO tr_prob(from_motion, to_motion, data) VALUES "
            + ",".join(values)
        )

        # INSERT INTO gaussian
        values = []
        avrs = area.gaussian.avrs
        covars = area.gaussian.covars
        for i, mid in enumerate(motion_ids):
            values.append(
                "(%d,%f,%f,%f,%f,%f)" % (
                    mid,
                    avrs[i,0], avrs[i,1], covars[i,0], covars[i,1], covars[i,2]
                )
            )
        self._cur.execute(
            "INSERT INTO gaussian(" \
            "motion, avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            ") VALUES "
            + ",".join(values)
        )

        # INSERT INTO sample_elem
        values = []
        for i1, sid in enumerate(sample_ids):
            for i2, mid in enumerate(motion_ids):
                values.append(
                    "(%d,%d,%f)" % (sid, mid, area.sample[i1,i2])
                )
        self._cur.execute(
            "INSERT INTO sample_elem(sample, motion, data) VALUES "
            + ",".join(values)
        )

        self._con.commit()

        # INSERT INTO history
        self.insert_history(aid, "init")

        return aid


    def insert_history(self, area_id:int, comment:str):
        self._cur.execute(
            "INSERT INTO history(area, time, comment) VALUES (%d,datetime('now'),'%s')"
            % (area_id , comment)
        )
        self._con.commit()


    def get_when_latest_history(self, area_id:int, hour_diff_from_utc:int) -> datetime.datetime:
        self._cur.execute("SELECT MAX(datetime) FROM history WHERE area=%d" % area_id)
        return self._cur.fetchone()[0] + datetime.timedelta(hours=hour_diff_from_utc)


    def get_area_id(self, name:str) -> int:
        self._cur.execute("SELECT id FROM area WHERE name='%s'" % name)
        result = self._cur.fetchall()
        if len(result) == 0:
            raise UnexistRecord("no record s.t. name='%s'" % name)
        return result[0][0]


    def get_area_meta(self, area_id:int) -> tuple[str, Floor]:
        self._cur.execute(
            "SELECT name, xmin, xmax, ymin, ymax FROM area WHERE id={}"\
            .format(area_id)
        )
        result = self._cur.fetchone()
        return result[0], Floor(result[1], result[2], result[3], result[4])


    def check_record_exist(self, table:str, id:int) -> bool:
        self._cur.execute("SELECT id FROM %s WHERE id=%d" % (table, id))
        return not self._cur.fetchone() is None


    def get_motion_num(self, area_id:int) -> int:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute("SELECT COUNT(id) FROM motion WHERE area=%d" % area_id)
        return self._cur.fetchone()[0]


    def get_motion_ids(self, area_id:int) ->list[int]:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute(
            "SELECT id FROM motion " \
            "WHERE area={} " \
            "ORDER BY id"\
            .format(area_id)
        )
        return [record[0] for record in self._cur.fetchall()]


    def get_sample_ids(self, area_id:int) -> list[int]:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute(
            "SELECT id FROM sample " \
            "WHERE area={} " \
            "ORDER BY id"\
            .format(area_id)
        )
        return [record[0] for record in self._cur.fetchall()]


    def get_init_prob_one(self, motion_id:int) -> float:
        if not self.check_record_exist("motion", motion_id):
            raise UnexistRecord(table="motion", columns=["id"], values=[motion_id])
        self._cur.execute(
            "SELECT data" \
            " FROM init_prob" \
            " WHERE motion={}"\
            .format(motion_id)
        )
        return self._cur.fetchall()[0][0]
    

    def get_init_prob_all(self, area_id:int) -> ndarray:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute(
            "SELECT data" \
            " FROM init_prob" \
            " LEFT OUTER JOIN motion ON init_prob.motion=motion.id" \
            " WHERE area={}" \
            " ORDER BY motion"\
            .format(area_id)
        )
        return np.array(self._cur.fetchall(), dtype="float32").flatten()


    def get_tr_prob_one(self, from_motion_id:int, to_motion_id: int) -> float:
        if not self.check_record_exist("motion", from_motion_id):
            raise UnexistRecord(table="motion", columns=["id"], values=[from_motion_id])
        if not self.check_record_exist("motion", to_motion_id):
            raise UnexistRecord(table="motion", columns=["id"], values=[to_motion_id])
        self._cur.execute(
            "SELECT data" \
            " FROM tr_prob" \
            " WHERE from_motion={} AND to_motion={}"\
            .format(from_motion_id, to_motion_id)
        )
        return self._cur.fetchall()[0][0]


    def get_tr_prob_vec(self, from_motion_id:int) -> ndarray:
        if not self.check_record_exist("motion", from_motion_id):
            raise UnexistRecord(table="motion", columns=["id"], values=[from_motion_id])
        self._cur.execute(
            "SELECT data" \
            " FROM tr_prob" \
            " WHERE from_motion=%d" \
            " ORDER BY to_motion"
            % from_motion_id
        )
        return np.array(self._cur.fetchall(), dtype="float32").flatten()


    def get_tr_prob_mat(self, area_id:int) -> ndarray:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        n = self.get_motion_num(area_id)
        self._cur.execute(
            "SELECT data" \
            " FROM tr_prob" \
            " LEFT OUTER JOIN motion ON tr_prob.from_motion=motion.id" \
            " WHERE area=%d" \
            " ORDER BY from_motion, to_motion"
            % area_id
        )
        return np.array(self._cur.fetchall(), dtype="float32").reshape((n, n))


    def get_gaussian_one(self, motion_id:int) -> tuple[ndarray, ndarray]:
        if not self.check_record_exist("motion", motion_id):
            raise UnexistRecord(table="motion", columns=["id"], values=[motion_id])
        self._cur.execute(
            "SELECT avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            " FROM gaussian" \
            " WHERE motion=%d"
            % motion_id
        )
        result = np.array(self._cur.fetchall()[0], dtype="float32")
        avr = result[[0, 1]]
        covar = result[[2, 3, 4]]
        return avr, covar


    def get_gaussian_all(self, area_id:int) -> Gaussian:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute(
            "SELECT avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            " FROM gaussian" \
            " LEFT OUTER JOIN motion ON gaussian.motion=motion.id" \
            " WHERE area=%d" \
            " ORDER BY motion"
            % area_id
        )
        result = np.array(self._cur.fetchall(), dtype="float32")
        avrs = result[:, [0, 1]]
        covars = result[:,[2, 3, 4]]
        return Gaussian(avrs, covars)


    def get_samples(self, area_id:int) -> ndarray:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute(
            "SELECT se.data" \
            " FROM sample_elem AS se" \
            " LEFT OUTER JOIN sample AS s ON se.sample=s.id" \
            " WHERE s.area={}" \
            " ORDER BY se.sample, se.motion"
            .format(area_id)
        )
        result = self._cur.fetchall()
        motion_num = self.get_motion_num(area_id)
        sample_num = int(len(result) / motion_num)
        samples = np.array(result, dtype=np.float32).reshape((sample_num, motion_num))
        return samples


    def get_dens_samples(self, area_id:int) -> ndarray:
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        self._cur.execute(
            "SELECT dens" \
            " FROM sample" \
            " WHERE area={}" \
            " ORDER BY id"
            .format(area_id)
        )
        result = self._cur.fetchall()
        sample_num = len(result)
        dens_samples = np.array(result, dtype=np.float32).reshape((sample_num,))
        return dens_samples


    def set_init_prob(self, area_id:int, init_prob:ndarray):
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        motion_ids = self.get_motion_ids(area_id)
        for i, mid in enumerate(motion_ids):
            self._cur.execute(
                "UPDATE init_prob" \
                " SET data=%f" \
                " WHERE motion=%d"
                % (init_prob[i], mid)
            )
        self._con.commit()


    def set_tr_prob(self, area_id:int, tr_prob:ndarray):
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        motion_ids = self.get_motion_ids(area_id)
        for i1, mid1 in enumerate(motion_ids):
            for i2, mid2 in enumerate(motion_ids):
                self._cur.execute(
                    "UPDATE init_prob" \
                    " SET data=%f" \
                    " WHERE from_motion=%d AND to_motion=%d"
                    % (tr_prob[i1, i1], mid1, mid2)
                )
        self._con.commit()


    def set_gaussian(self, area_id:int, gaussian:Gaussian):
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        motion_ids = self.get_motion_ids(area_id)
        for i, mid in enumerate(motion_ids):
            self._cur.execute(
                "UPDATE init_prob" \
                " SET avr_x=%f, avr_y=%f, xovar_xx=%f, covar_xy=%f, covar_yy=%f" \
                " WHERE motion=%d"
                % (
                    gaussian.avrs[i,0], gaussian.avrs[i,1],
                    gaussian.covars[i,0], gaussian.covars[i,0], gaussian.covars[i,1], gaussian.covars[i,2],
                    mid
                )
            )
        self._con.commit()


    def set_dens_samples(self, area_id:int, dens_samples:ndarray):
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        sample_ids = self.get_sample_ids(area_id)
        for i, sid in enumerate(sample_ids):
            self._cur.execute(
                "UPDATE sample SET dens={} WHERE id={}"\
                .format(dens_samples[i], sid)
            )
        self._con.commit()


    def reinit_area(self, area_id:int, area:Area):
        if not self.check_record_exist("area", area_id):
            raise UnexistRecord(table="area", columns=["id"], values=[area_id])
        motion_ids = self.get_motion_ids(area_id)

        # DELETE
        self._cur.execute(
            "DELETE FROM init_prob WHERE motion IN " \
            "(SELECT id FROM motion WHERE area={})".format(area_id)
        )
        self._cur.execute(
            "DELETE FROM tr_prob WHERE to_motion IN " \
            "(SELECT id FROM motion WHERE area={})".format(area_id)
        )
        self._cur.execute(
            "DELETE FROM gaussian WHERE motion IN " \
            "(SELECT id FROM motion WHERE area={})".format(area_id)
        )
        self._cur.execute(
            "DELETE FROM sample_elem WHERE motion IN " \
            "(SELECT id FROM motion WHERE area={})".format(area_id)
        )
        self._cur.execute("DELETE FROM sample WHERE area={}".format(area_id))
        self._cur.execute("DELETE FROM motion WHERE area={}".format(area_id))

        # UPDATE area
        f = area.floor
        self._cur.execute(
            "UPDATE area SET name='{}',xmin={},xmax={},ymin={},ymax={} WHERE id={}"\
            .format(area.name, f.xmin, f.xmax, f.ymin, f.ymax, area_id)
        )

        # INSERT INTO motion
        values = ["(%d)" % area_id] * area.motion_num
        self._cur.execute("INSERT INTO motion(area) VALUES " + ",".join(values))
        self._con.commit()
        motion_ids = self.get_motion_ids(area_id)

        # INSERT INTO sample
        values = []
        for d in area.dens_sample.tolist():
            values.append("({},{})".format(d, area_id))
        self._cur.execute(
            "INSERT INTO sample(dens, area) VALUES"
            + ",".join(values)
        )
        self._con.commit()
        sample_ids = self.get_sample_ids(area_id)

        # INSERT INTO init_prob
        values = []
        for i, mid in enumerate(motion_ids):
            values.append("(%d,%f)" % (mid, area.init_prob[i]))
        self._cur.execute(
            "INSERT INTO init_prob(motion, data) VALUES "
            + ",".join(values)
        )

        # INSERT INTO tr_prob
        values = []
        for i1, mid1 in enumerate(motion_ids):
            for i2, mid2 in enumerate(motion_ids):
                values.append("(%d,%d,%f)" % (mid1, mid2, area.tr_prob[i1,i2]))
        self._cur.execute(
            "INSERT INTO tr_prob(from_motion, to_motion, data) VALUES "
            + ",".join(values)
        )

        # INSERT INTO gaussian
        values = []
        avrs = area.gaussian.avrs
        covars = area.gaussian.covars
        for i, mid in enumerate(motion_ids):
            values.append(
                "(%d,%f,%f,%f,%f,%f)" % (
                    mid,
                    avrs[i,0], avrs[i,1], covars[i,0], covars[i,1], covars[i,2]
                )
            )
        self._cur.execute(
            "INSERT INTO gaussian(" \
            "motion, avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            ") VALUES "
            + ",".join(values)
        )

        # INSERT INTO sample_elem
        values = []
        for i1, sid in enumerate(sample_ids):
            for i2, mid in enumerate(motion_ids):
                values.append(
                    "(%d,%d,%f)" % (sid, mid, area.sample[i1,i2])
                )
        self._cur.execute(
            "INSERT INTO sample_elem(sample, motion, data) VALUES "
            + ",".join(values)
        )

        self._con.commit()

        # INSERT INTO history
        self.insert_history(area_id, "reinit")

