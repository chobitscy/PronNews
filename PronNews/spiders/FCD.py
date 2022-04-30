import scrapy
from bs4 import BeautifulSoup

from PronNews.items.nyaa import Nyaa
from PronNews.mixin.dateMixin import DataMixin


class FCDSpider(scrapy.Spider, DataMixin):
    name = 'FCD'
    allowed_domains = ['adult.contents.fc2.com']
    base_url = 'https://adult.contents.fc2.com/article/%s/'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCD.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT vid FROM video WHERE create_date is NULL AND state = 1"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            vid = result['vid']
            yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'vid': vid})

    def parse(self, response, **kwargs):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'lxml')
        screenshot_list = soup.select('.items_article_SampleImagesArea img')
        screenshot = ','.join([n.get('src')[35:] for n in screenshot_list]) if len(screenshot_list) != 0 else ''
        thumb_ele = soup.select('.items_article_MainitemThumb img')
        thumb = thumb_ele[0].get('src') if len(thumb_ele) > 0 else None
        tags = ','.join([n.get_text() for n in soup.select('.tagTag')])
        create_date_ele = soup.select('.items_article_Releasedate p')
        create_date = create_date_ele[0].get_text().split(':')[1].strip() if len(create_date_ele) > 0 else None
        product_ele = soup.select('.items_article_StarA+ li a')
        product, product_home = product_ele[0].get_text(), product_ele[0].get('href') if len(product_ele) != 0 else None
        info = Nyaa()
        info['vid'] = meta['vid']
        info['screenshot'] = screenshot
        info['thumb'] = thumb
        info['product'] = product
        info['product_home'] = product_home
        info['tid'] = tags
        info['create_date'] = create_date
        yield info

    def close(self, spider, reason):
        super().flushall()
