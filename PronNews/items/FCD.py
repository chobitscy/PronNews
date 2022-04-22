#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy

from PronNews.items.base import base


class FCD(base):
    screenshot = scrapy.Field()
    thumb = scrapy.Field()
    author = scrapy.Field()
    author_home = scrapy.Field()
    tags = scrapy.Field()
    create_date = scrapy.Field()
