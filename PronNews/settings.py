# Scrapy settings for sipderTest project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('config.ini', encoding='utf-8')
db_host, db_port = cfg.get('db', 'host'), cfg.getint('db', 'port')
db_user, db_password, db_name = cfg.get('db', 'user'), cfg.get('db', 'password'), cfg.get('db', 'name')
env = cfg.get('server', 'env')
scrapyd_host, scrapyd_port = cfg.get('scrapyd', 'host'), cfg.get('scrapyd', 'port')
scrapyd_auth = cfg.get('scrapyd', 'auth')
redis_host, redis_port = cfg.get('redis', 'host'), cfg.getint('redis', 'port')
redis_user, redis_password, redis_db = cfg.get('redis', 'user'), cfg.get('redis', 'password'), cfg.getint('redis', 'db')
update = cfg.get('server', 'update')
auth = cfg.get('server', 'auth')
master = cfg.getboolean('server', 'master')

BOT_NAME = 'PronNews'

SPIDER_MODULES = ['PronNews.spiders']
NEWSPIDER_MODULE = 'PronNews.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'sipderTest.middlewares.SipdertestSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
if env == 'dev':
    DOWNLOADER_MIDDLEWARES = {
        'PronNews.middlewares.ProxyMiddleware': 500,
    }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'PronNews.pipelines.nyaa.Pipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Custom config
# Proxy
PROXY = {
    'host': '127.0.0.1',
    'port': 1081
}

# DB
MYSQL = {
    'host': db_host,
    'port': db_port,
    'user': db_user,
    'passwd': db_password,
    'db': db_name,
    'charset': 'utf8',
}

SCRAPYD = [{
    'host': scrapyd_host,
    'port': scrapyd_port,
    'auth': scrapyd_auth
}, {
    'host': scrapyd_host,
    'port': scrapyd_port,
    'auth': scrapyd_auth
}]

REDIS = {
    'host': redis_host,
    'port': redis_port,
    'user': redis_user,
    'password': redis_password,
    'db': redis_db
}

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

UPDATE = update
AUTH = auth

MASTER = master
