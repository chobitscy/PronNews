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
    rate = scrapy.Field()
    print_screen = scrapy.Field()
    screenshot = scrapy.Field()
    thumb = scrapy.Field()
    product = scrapy.Field()
    product_home = scrapy.Field()
    tags = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    product_avatar = scrapy.Field()