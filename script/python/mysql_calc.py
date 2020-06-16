# -*- coding: utf-8
# File : mysql_calc.py
# Author : 23021040@163.com
import json
import pymysql
import pandas as pd

MYSQL_CONFIG = {
    "host": "192.168.1.139",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "dbschema": 'hys',
    "charset": 'utf8'
}


def main():
    dataSum = []
    single = MYSQL_CONFIG
    conn = pymysql.connect(host=single.get('host'), port=single.get('port'), user=single.get('user'),
                           passwd=single.get('password'), charset=single.get('charset'))
    # 表信息
    sql = "select " \
          "table_name as 'table_name', " \
          "TABLE_ROWS as 'rows'," \
          "DATA_LENGTH as 'data_size', " \
          "INDEX_LENGTH as 'index_size' " \
          "from information_schema.tables " \
          "where TABLE_SCHEMA='" + single['dbschema'] + "'"
    df = pd.read_sql(sql, conn)
    print('-' * 30)
    print(str(df))


    for t in df.table_name:
        sql = "select " \
              "column_name, " \
              "data_type," \
              "CHARACTER_MAXIMUM_LENGTH as 'length', " \
              "CHARACTER_OCTET_LENGTH as 'octet', " \
              "CHARACTER_SET_NAME as 'encode' " \
              "from information_schema.COLUMNS " \
              "where TABLE_SCHEMA='" + single['dbschema'] + "' and table_name='" + t + "'"
        columns = pd.read_sql(sql, conn)
        print('-' * 30)
        print(str(columns))
    conn.close()


if __name__ == '__main__':
    print("***一次性统计所有对接数据的委办局，和其对应的数据（条数）***")
    main()
