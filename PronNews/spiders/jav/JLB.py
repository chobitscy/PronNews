import scrapy
from bs4 import BeautifulSoup

from PronNews.items.nyaa import Nyaa
from PronNews.mixin.dateMixin import DataMixin


class JibSpider(scrapy.Spider, DataMixin):
    name = 'JLB'
    allowed_domains = ['javlibrary.com']
    base_site = 'https://www.javlibrary.com/cn/vl_searchbyid.php?keyword=%s'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCD.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SElECT a.vid AS vid,b.url AS url FROM video AS a LEFT JOIN redirect AS b ON a.vid = b.vid WHERE " \
              "a.pub_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND NOW() " \
              "AND state = 1 AND (type_id = 2 OR type_id = 3)"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            vid = result['vid']
            redirect_url = result['url']
            url = self.base_site % vid if redirect_url is None else redirect_url
            yield scrapy.Request(url, callback=self.parse, meta={'vid': vid, 'redirect': redirect_url is None})

    def parse(self, response, **kwargs):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'lxml')
        screenshot = ','.join([n.get('src') for n in soup.select('.previewthumbs > img')])
        thumb_ele = soup.select('#video_jacket_img')
        thumb = thumb_ele[0].get('src') if len(thumb_ele) != 0 else None
        author_ele = soup.select('#video_cast a')
        author = ','.join([n.get_text() for n in author_ele])
        author_home = ','.join([n.get('href') for n in author_ele])
        tags = ','.join([n.get_text() for n in soup.select('#video_genres a')])
        create_date_ele = soup.select('#video_date .text')
        create_date = create_date_ele[0].get_text() if len(create_date_ele) != 0 else ''
        rate_ele = soup.select('.score')
        rate = rate_ele[0].get_text() if len(rate_ele) != 0 else 0
        product_ele = soup.select('#video_maker a')
        product = product_ele[0].get_text() if len(product_ele) != 0 else None
        info = Nyaa()
        info['vid'] = meta['vid']
        info['rate'] = rate
        info['screenshot'] = screenshot
        info['thumb'] = thumb
        info['author'] = author
        info['author_home'] = author_home
        info['tags'] = tags
        info['create_date'] = create_date
        info['url'] = response.url if meta['redirect'] else None
        info['product'] = product
        yield info
