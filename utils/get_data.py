import pymysql

from settings import db


class GetData:
    def __init__(self, host=db['host'], port=3306, user=db['user'], passwd=db['password'], db=db['dbname'], charset="utf8"):
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset="utf8")
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def get_data(self, keyword, table_name=db['table_name']):
        sql = 'SELECT price, est_sales, reviews_30d from {table_name} WHERE keyword="{keyword}"'.format(table_name=table_name, keyword=keyword)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if results:
            return results
        else:
            print(results)
            raise KeyError

    def close(self):
        self.cursor.close()
        self.conn.close()


