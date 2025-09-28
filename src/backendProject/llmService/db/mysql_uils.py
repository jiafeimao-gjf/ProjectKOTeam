from sqlalchemy.dialects.mysql import pymysql


def getDb():
    db = pymysql.connect(host='localhost', user='root', password='123456', db='llm_chat_history')
    return db


mysql_db = getDb()
