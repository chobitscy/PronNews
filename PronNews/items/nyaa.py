import scrapy

from PronNews.items.base import base


class Nyaa(base):
    title = scrapy.Field()
    pub_date = scrapy.Field()
    info_hash = scrapy.Field()
    size = scrapy.Field()
    speeders = scrapy.Field()
    downloads = scrapy.Field()
    completed = scrapy.Field()
