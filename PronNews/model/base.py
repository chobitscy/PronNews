#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import BigInteger, Column, DateTime, Integer

class Base(object):
    id = Column(BigInteger, primary_key=True)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    state = Column(Integer)
