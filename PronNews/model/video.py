#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, Float
from sqlalchemy.ext.declarative import declarative_base

from PronNews.model.base import Base

basics = declarative_base()


class Video(basics, Base):
    __tablename__ = 'video'
    vid = Column(String)
    title = Column(String)
    pub_date = Column(DateTime)
    info_hash = Column(String)
    size = Column(Float)
    speeders = Column(Integer)
    downloads = Column(Integer)
    completed = Column(Integer)
    rate = Column(Float)
    print_screen = Column(String)
    screenshot = Column(Text)
    thumb = Column(String)
    create_date = Column(DateTime)
    pid = Column(BigInteger)
    tid = Column(Text)
    aid = Column(BigInteger)
    comments = Column(Integer)
    likes = Column(Integer)
