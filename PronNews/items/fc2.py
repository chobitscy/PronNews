#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy

from PronNews.items.base import base


class Fc2(base):
    rate = scrapy.Field()
    screenshot = scrapy.Field()
    thumb = scrapy.Field()