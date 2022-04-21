import datetime

from twisted.enterprise import adbapi

from PronNews.utils import get_snowflake_uuid


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
        now = datetime.datetime.now()
        # 如果数据存在，更新上传量、下载量、完成量
        if result:
            item['update_time'] = now
            sql = "UPDATE video SET speeders = '%s', downloads = '%s', completed = '%s',update_time = '%s' " \
                  "WHERE id = '%s'"
            par = (item['speeders'], item['downloads'], item['completed'], item['update_time'], result[0][0])
            state = self.db_pool.runQuery(sql % par)
        # 如果数据不存在，新增
        else:
            item['id'] = get_snowflake_uuid()
            item['create_time'] = now
            item['update_time'] = now
            item['state'] = 1
            state = self.db_pool.runInteraction(self.do_insert, item)
        state.addErrback(self.handle_error, item, spider)

    # 错误处理
    @staticmethod
    def handle_error(failure, item, spider):
        print(failure)

    def process_item(self, item, spider):
        query = self.db_pool.runQuery('SELECT id from video WHERE vid = %s' % item['vid'])
        query.addCallback(self.filer_item, item, spider)
        query.addErrback(self.handle_error, item, spider)

    @staticmethod
    def do_insert(cursor, item):
        insert_sql = """
                insert into video( 
                id, 
                vid,
                title,
                pub_date, 
                info_hash, 
                size, 
                speeders,
                downloads,
                completed,
                create_time,
                update_time,
                state)
                values (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
                """
        params = (item['id'],
                  item['vid'],
                  item['title'],
                  item['pub_date'],
                  item['info_hash'],
                  item['size'],
                  item['speeders'],
                  item['downloads'],
                  item['completed'],
                  item['create_time'],
                  item['update_time'],
                  item['state'])
        cursor.execute(insert_sql, params)