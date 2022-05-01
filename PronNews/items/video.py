import scrapy

from PronNews.items.base import base


class Video(base):
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
    tid = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    product_avatar = scrapy.Field()
    pid = scrapy.Field()
    comments = scrapy.Field()
    likes = scrapy.Field()
