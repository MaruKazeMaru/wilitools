# SPDX-FileCopyrightText: 2024 ShinagwaKazemaru
# SPDX-License-Identifier: MIT License

from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class AreaModel(Base):
    __tablename__ = 'area'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    # meta
    name = Column('name', String(32))
    # floor
    x_min = Column('x_min', Float)
    x_max = Column('x_max', Float)
    y_min = Column('y_min', Float)
    y_max = Column('y_max', Float)
    #relation
    motion = relationship('MotionModel', cascade='all, delete-orphan')
    sample = relationship('SampleModel', cascade='all, delete-orphan')


class MotionModel(Base):
    __tablename__ = 'motion'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    area = Column('area', Integer, ForeignKey('area.id'))
    # meta
    name = Column('name', String(32), default='')
    # gaussian
    avr_x = Column('avr_x', Float)
    avr_y = Column('avr_y', Float)
    covar_xx = Column('covar_xx', Float)
    covar_xy = Column('covar_xy', Float)
    covar_yy = Column('covar_yy', Float)
    # relation
    init_prob = relationship('InitProbModel', cascade='all, delete-orphan')
    tr_prob   = relationship('TrProbModel', cascade='all, delete-orphan')
    miss_prob = relationship('MissProbModel', cascade='all, delete-orphan')


class InitProbModel(Base):
    __tablename__ = 'init_prob'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    motion = Column('motion', Integer, ForeignKey('motion.id'), unique=True)
    data = Column('data', Float)


class TrProbModel(Base):
    __tablename__ = 'tr_prob'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    from_motion = Column('from_motion', Integer, ForeignKey('motion.id'))
    to_motion   = Column('to_motion',   Integer)
    # ---memo-------
    # multi foreign key reference to one table
    # => error OR cascade not working
    # --------------
    __table_args__ = (UniqueConstraint('from_motion', 'to_motion'),)
    data = Column('data', Float)


class SampleModel(Base):
    __tablename__ = 'sample'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    area = Column('area', Integer, ForeignKey('area.id'))
    dens = Column('dens', Float) #probability density
    miss_prob = relationship('MissProbModel')


class MissProbModel(Base):
    __tablename__ = 'miss_prob'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    sample = Column('sample', Integer, ForeignKey('sample.id'))
    motion = Column('motion', Integer, ForeignKey('motion.id'))
    __table_args__ = (UniqueConstraint('sample', 'motion'),)
    data = Column('data', Float)
