#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy

from PronNews.items.base import base


class jav_torrent(base):
    print_screen = scrapy.Field()