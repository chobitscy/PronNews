import datetime

from twisted.enterprise import adbapi


class Pipeline(object):

    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        db_params = settings.get('MYSQL')
        db_pool = adbapi.ConnectionPool('pymysql', **db_params)
        return cls(db_pool)

    # 数据过滤
    def filer_item(self, result, item, spider):
        if item['create_date'] is not None:
            sql = "UPDATE video SET screenshot = '%s',thumb = '%s',author = '%s',author_home = '%s'" \
                  ",tags = '%s',create_date= '%s',update_time = '%s',product = '%s' WHERE id = '%s'"
            par = (item['screenshot'], item['thumb'], item['author'], item['author_home'], item['tags'],
                   item['create_date'], datetime.datetime.now(), item['product'], result[0][0])
            if item['url'] is not None:
                self.db_pool.runQuery("INSERT INTO redirect(vid,url) VALUES('%s','%s')" % (item['vid'], item['url']))
        else:
            sql = "UPDATE video SET state = -1 WHERE id = '%s'"
            par = result[0][0]
        state = self.db_pool.runQuery(sql % par)
        state.addErrback(self.handle_error, item, spider)

    # 错误处理
    @staticmethod
    def handle_error(failure, item, spider):
        print(failure)

    def process_item(self, item, spider):
        query = self.db_pool.runQuery("SELECT id from video WHERE vid = '2825898'")
        query.addCallback(self.filer_item, item, spider)
        query.addErrback(self.handle_error, item, spider)
