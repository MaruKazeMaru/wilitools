import os
import datetime
import sqlite3

import numpy as np
from numpy import ndarray

from area import Area
from mathf.gaussian import Gaussian
from .exceptions import UnexistRecord

class WiliDB:
    def __init__(self, db_path:str):
        already_exist = os.path.exists(db_path)
        self._con = sqlite3.connect(db_path)
        self._cur = self._con.cursor()
        if not already_exist:
            self._create_tables()


    def __del__(self):
        self._con.close()
        super().__del__()


    def _create_tables(self):
        # CREATE TABLES
        self._cur.execute("PRAGMA foreign_keys=true")
        self._cur.execute(
            "CREATE TABLE area(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "name TEXT," \
            "UNIQUE(name)"
            ")"
        )
        self._cur.execute(
            "CREATE TABLE motion(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "area INTEGER," \
            "FOREIGN KEY(area) REFERENCES area(id)" \
            ")"
        )
        self._cur.execute(
            "CREATE TABLE init_prob(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "area INTEGER," \
            "motion INTEGER," \
            "data REAL," \
            "FOREIGN KEY(area) REFERENCES area(id)," \
            "FOREIGN KEY(motion) REFERENCES motion(id)," \
            "UNIQUE(area,motion)"
            ")"
        )
        self._cur.execute(
            "CREATE TABLE tr_prob(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "area INTEGER," \
            "from_motion INTEGER," \
            "to_motion INTEGER," \
            "data REAL," \
            "FOREIGN KEY(area) REFERENCES area(id)," \
            "FOREIGN KEY(from_motion) REFERENCES motion(id)," \
            "FOREIGN KEY(to_motion) REFERENCES motion(id)," \
            "UNIQUE(area,from_motion,to_motion)"
            ")"
        )
        self._cur.execute(
            "CREATE TABLE gaussian(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "area INTEGER," \
            "motion INTEGER," \
            "avr_x REAL," \
            "avr_y REAL," \
            "covar_xx REAL," \
            "covar_xy REAL," \
            "covar_yy REAL," \
            "FOREIGN KEY(area) REFERENCES area(id)," \
            "FOREIGN KEY(motion) REFERENCES motion(id)," \
            "UNIQUE(area,motion)"
            ")"
        )
        self._cur.execute(
            "CREATE TABLE history(" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "area INTEGER," \
            "time DATETIME,"
            "comment TEXT,"
            "FOREIGN KEY(area) REFERENCES area(id)" \
            ")"
        )
        self._con.commit()


    def initialize_area(self, area:Area):
        self._cur.execute("INSERT INTO area(name) VALUES ('%s')" % area.name)
        self._con.commit()

        self._cur.execute("SELECT id WHERE name='%s'" % area.name)
        area_id = self._cur.fetchone()[0]

        # INSERT INTO motion
        values = ["(%d)" % area_id] * area.motion_num
        self._cur.execute("INSERT INTO motion(area) VALUES " + ",".join(values))

        # INSERT INTO init_prob
        values = []
        for i in range(area.motion_num):
            values.append("(%d,%d,%f)" % (area_id, i, area.init_prob[i]))
        self._cur.execute(
            "INSERT INTO tr_prob(area, motion, data) VALUES "
            + ",".join(values)
        )

        # INSERT INTO tr_prob
        values = []
        for i in range(area.motion_num):
            for j in range(area.motion_num):
                values.append("(%d,%d,%d,%f)" % (area_id, i, j, area.tr_prob[i,j]))
        self._cur.execute(
            "INSERT INTO tr_prob(area, from_motion, to_motion, data) VALUES "
            + ",".join(values)
        )

        # INSERT INTO gaussian
        values = []
        avrs = area.gaussian.avrs
        covars = area.gaussian.covars
        for i in range(area.motion_num):
            values.append(
                "(%d,%d,%f,%f,%f,%f,%f)" % (
                    area_id, i,
                    avrs[i,0], avrs[i,1], covars[i,0], covars[i,1], covars[i,2]
                )
            )
        self._cur.execute(
            "INSERT INTO gaussian(" \
            "area, motion, avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            ") VALUES "
            + ",".join(values)
        )
        self._con.commit()

        # INSERT INTO history
        self.set_history(area_id, "init")


    def set_history(self, area_id:int, comment:str):
        self._cur.execute(
            "INSERT INTO history(area, time, comment) VALUES (%d,datetime('now'),'%s')"
            % (area_id , comment)
        )
        self._con.commit()


    def get_when_latest_history(self, area_id:int, hour_diff_from_utc:int) -> datetime.datetime:
        self._cur.execute("SELECT MAX(datetime) FROM history WHERE area=%d" % area_id)
        return self._cur.fetchone()[0] + datetime.timedelta(hours=hour_diff_from_utc)


    def get_area_id(self, name:str) -> Area:
        self._cur.execute("SELECT id FROM area WHERE name='%s'" % name)
        result = self._cur.fetchall()
        if len(result) == 0:
            raise UnexistRecord("no record s.t. name='%s'" % name)
        return result[0][0]


    def get_motion_num(self, area_id:int) -> int:
        self._cur.execute("SELECT COUNT(id) FROM motion WHERE area=%d" % area_id)
        return self._cur.fetchone()[0]


    def get_tr_prob_one(self, area_id:int, from_motion_id:int, to_motion_id: int) -> float:
        self._cur.execute(
            "SELECT data" \
            " FROM tr_prob" \
            " WHERE are=%d AND from_motion=%d AND to_motion=%d"
            % (area_id, from_motion_id, to_motion_id)
        )
        return self._cur.fetchall()[0][0]


    def get_tr_prob_vec(self, area_id:int, from_motion_id:int) -> ndarray:
        self._cur.execute(
            "SELECT data" \
            " FROM tr_prob" \
            " WHERE area=%d AND from_motion=%d" \
            " ORDER BY to_motion"
            % (area_id, from_motion_id)
        )
        return np.array(self._cur.fetchall(), dtype="float32").flatten()


    def get_tr_prob_mat(self, area_id) -> ndarray:
        n = self.get_motion_num(area_id)
        self._cur.execute(
            "SELECT data" \
            " FROM tr_prob" \
            " WHERE area=%d" \
            " ORDER BY from_motion, to_motion"
            % (area_id)
        )
        return np.array(self._cur.fetchall(), dtype="float32").reshape((n, n))


    def get_gaussian_one(self, area_id:int, motion_id:int) -> tuple[ndarray, ndarray]:
        self._cur.execute(
            "SELECT avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            " FROM gaussian" \
            " WHERE area=%d AND motion=%d"
            % (area_id, motion_id)
        )
        result = np.array(self._cur.fetchall()[0], dtype="float32")
        avr = result[[0, 1]]
        covar = result[[2, 3, 4]]
        return avr, covar


    def get_gaussian_all(self, area_id:int) -> Gaussian:
        self._cur.execute(
            "SELECT avr_x, avr_y, covar_xx, covar_xy, covar_yy" \
            " FROM gaussian" \
            " WHERE area=%d" \
            " ORDER BY motion"
            % (area_id)
        )
        result = np.array(self._cur.fetchall(), dtype="float32")
        avrs = result[:, [0, 1]]
        covars = result[:,[2, 3, 4]]
        return Gaussian(avrs, covars)


    def set_init_prob(self, area_id:int, init_prob:ndarray):
        n = init_prob.shape[0]
        for i in range(n):
            self._cur.execute(
                "UPDATE init_prob" \
                " SET data=%f" \
                " WHERE area=%d AND motion=%d"
                % (init_prob[i], area_id, i)
            )


    def set_tr_prob(self, area_id:int, tr_prob:ndarray):
        n = tr_prob.shape[0]
        for i in range(n):
            for j in range(n):
                self._cur.execute(
                    "UPDATE init_prob" \
                    " SET data=%f" \
                    " WHERE area=%d AND from_motion=%d AND to_motion=%d"
                    % (tr_prob[i, j], area_id, i, j)
                )


    def set_gaussian(self, area_id:int, gaussian:Gaussian):
        n = gaussian.avrs.shape[0]
        for i in range(n):
            self._cur.execute(
                "UPDATE init_prob" \
                " SET avr_x=%f, avr_y=%f, xovar_xx=%f, covar_xy=%f, covar_yy=%f" \
                " WHERE area=%d AND motion=%d"
                % (
                    gaussian.avrs[i,0], gaussian.avrs[i,1],
                    gaussian.covars[i,0], gaussian.covars[i,0], gaussian.covars[i,1], gaussian.covars[i,2],
                    area_id, i
                )
            )
