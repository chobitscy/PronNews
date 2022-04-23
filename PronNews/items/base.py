#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy


class base(scrapy.Item):
    id = scrapy.Field()
    vid = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    state = scrapy.Field()
    type_id = scrapy.Field()
