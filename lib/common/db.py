#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import psycopg2
import urlparse

class DB(object):
    table_name = NotImplementedError

    def __init__(self):
        urlparse.uses_netloc.append("postgres")
        url = urlparse.urlparse(os.environ["DATABASE_URL"])

        self.conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.conn.autocommit = True
        print "set the auto-commit mode for {}".format(self.table_name)

        self.create_table()

    def create_table(self):
        raise NotImplementedError

    def ask(self, user_id, user_name, question, answer):
        raise NotImplementedError

    def query(self, user_id=None):
        cursor = self.conn.cursor()

        sql = "SELECT * FROM {} ORDER BY creation_datetime DESC".format(self.table_name)
        if user_id is not None:
            sql = "SELECT * FROM {} WHERE user_id = '{}' ORDER BY creation_datetime DESC;".format(self.table_name, user_id)

        cursor.execute(sql)
        for row in cursor.fetchall():
            yield row

        cursor.close()

    def delete(self):
        sql = "DELETE FROM {}".format(self.table_name)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        cursor.close()

    def drop(self):
        sql = "DROP TABLE {}".format(self.table_name)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        cursor.close()

    def close(self):
        self.conn.close()
