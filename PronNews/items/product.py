import scrapy

from PronNews.items.base import base


class Product(base):
    name = scrapy.Field()
    home = scrapy.Field()
    avatar = scrapy.Field()
    works = scrapy.Field()
    fans = scrapy.Field()
