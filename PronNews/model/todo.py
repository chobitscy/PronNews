#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

basics = declarative_base()


class Todo(basics):
    __tablename__ = 'todo'
    vid = Column(Integer, primary_key=True)
    create_time = Column(DateTime)

    def __init__(self, vid):
        self.vid = vid
        self.create_time = datetime.datetime.now()
