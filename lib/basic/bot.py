#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Bot(object):
    repository = "Bot"
    filename = "bot.json"

    def __init__(self):
        self.dataset = []
        self.info = {}

        self.init(True)

    def init(self, is_gen):
        self.set_dataset()
        #self.crawl_job(is_gen)
        self.gen_results()

    def set_dataset(self):
        raise NotImplementedError

    def crawl_job(self, is_gen=False):
        raise NotImplementedError

    def gen_results(self):
        raise NotImplementedError

    def bots(self, msg):
        raise NotImplementedError
