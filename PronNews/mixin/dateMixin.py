#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
from redis import StrictRedis

from PronNews import settings


class DataMixin(object):

    def __init__(self):
        self.results = []

    def custom(self, sql):
        db_config = settings.MYSQL
        host = db_config['host']
        port = db_config['port']
        user = db_config['user']
        password = db_config['passwd']
        db = db_config['db']
        connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                  cursorclass=pymysql.cursors.DictCursor)
        cursor = connect.cursor()
        cursor.execute(sql)
        self.results = cursor.fetchall()
        cursor.close()
        connect.close()

    def flushall(self):
        _config = settings.REDIS
        redis = StrictRedis(host=_config['host'], port=_config['port'], username=_config['user'],
                            password=_config['password'], db=_config['db'], )
        redis.flushall()
        redis.close()

    @staticmethod
    def operation(sql):
        db_config = settings.MYSQL
        host = db_config['host']
        port = db_config['port']
        user = db_config['user']
        password = db_config['passwd']
        db = db_config['db']
        connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                  cursorclass=pymysql.cursors.DictCursor)
        cursor = connect.cursor()
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()
