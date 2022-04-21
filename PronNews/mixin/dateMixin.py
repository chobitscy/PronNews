#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql

from PronNews import settings


class DataMixin(object):

    def __init__(self):
        self.results = []

    def last_week_vid(self):
        db_config = settings.MYSQL
        host = db_config['host']
        port = db_config['port']
        user = db_config['user']
        password = db_config['passwd']
        db = db_config['db']
        connect = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                  cursorclass=pymysql.cursors.DictCursor)
        cursor = connect.cursor()
        cursor.execute("SELECT vid FROM video WHERE pub_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND NOW()")
        self.results = cursor.fetchall()
        cursor.close()
        connect.close()
