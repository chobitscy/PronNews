#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

from PronNews.model.base import Base
from PronNews.utils import get_snowflake_uuid

basics = declarative_base()


class Product(basics, Base):
    __tablename__ = 'product'
    name = Column(Text)
    home = Column(Text)
    avatar = Column(String)

    def __init__(self, name, home, avatar):
        self.name = name
        self.home = home
        self.avatar = avatar
        now = datetime.datetime.now()
        self.id = get_snowflake_uuid()
        self.create_time = now
        self.update_time = now
        self.state = 1
