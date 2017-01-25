#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import psycopg2
import urlparse
import datetime

from lib.common.utils import UTF8

class Bot(object):
    repository = "Bot"
    filename = "bot.json"

    def __init__(self):
        self.dataset = []
        self.info = {}

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

        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS {} (question VARCHAR(128), creation_datetime TIMESTAMP, answer TEXT);".format(self.repository))
        cursor.execute("CREATE INDEX IF NOT EXISTS {table_name}_idx ON {table_name} (creation_datetime, question);".format(table_name=self.repository))
        cursor.close()

        self.cursor = self.conn.cursor()

    def init(self):
        self.set_dataset()
        self.crawl_job()
        self.gen_results()
        self.insert_answer()

    def insert_answer(self):
        rows = []

        cursor = self.conn.cursor()
        for question, answer in self.info.items():
            try:
                rows.append("('{}', '{}', '{}')".format(question, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), json.dumps(answer)))
            except UnicodeDecodeError as e:
                rows.append("('{}', '{}', '{}')".format(question.encode(UTF8), datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), json.dumps(answer)))

        if rows:
            sql = "DELETE FROM {}".format(self.repository)
            cursor.execute(sql)

            sql = "INSERT INTO {} VALUES {}".format(self.repository, ",".join(rows))
            cursor.execute(sql)

            print "The {} bot finish updating answers".format(type(self).__name__)
        else:
            print "Found empty rows"

        cursor.close()

    def set_dataset(self):
        raise NotImplementedError

    def crawl_job(self, is_gen=False):
        raise NotImplementedError

    def gen_results(self):
        raise NotImplementedError

    def ask(self, question):
        creation_datetime, answer = None, None

        sql = "SELECT creation_datetime, answer FROM {} WHERE question = '{}' ORDER BY creation_datetime DESC LIMIT 1".format(self.repository, question)

        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            creation_datetime, answer = row
            answer = json.loads(answer)

        return creation_datetime, answer

    def bots(self, msg):
        raise NotImplementedError

    def close(self):
        self.conn.close()
