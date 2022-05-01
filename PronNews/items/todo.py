#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy


class Todo(scrapy.Item):
    id = scrapy.Field()
    vid = scrapy.Field()
