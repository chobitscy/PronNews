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
        sql = "UPDATE video SET print_screen = '%s',update_time = '%s' WHERE id = '%s'"
        par = (item['print_screen'], datetime.datetime.now(), result[0][0])
        state = self.db_pool.runQuery(sql % par)
        state.addErrback(self.handle_error, item, spider)

    # 错误处理
    @staticmethod
    def handle_error(failure, item, spider):
        print(failure)

    def process_item(self, item, spider):
        query = self.db_pool.runQuery('SELECT id from video WHERE vid = %s' % item['vid'])
        query.addCallback(self.filer_item, item, spider)
        query.addErrback(self.handle_error, item, spider)
