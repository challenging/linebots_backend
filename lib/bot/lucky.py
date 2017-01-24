#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import requests

from google.modules.utils import get_html
from bs4 import BeautifulSoup

from lib.common.bot import Bot
from lib.common.utils import UTF8, crawl, data_dir

from lib.langconv import *

class LuckyBot(Bot):
    repository = "lucky"
    filename = "lucky.json"

    def mapping(self, msg):
        msg = msg.lower()

        if re.search(r"^(山羊|摩羯|capricorn)", msg):
            msg = "capricorn"
        elif re.search(r"^(金牛|taurus)", msg):
            msg = "taurus"
        elif re.search(r"^(雙子|双子|gemini)", msg):
            msg = "gemini"
        elif re.search(r"^(巨蟹|cancer)", msg):
            msg = "cancer"
        elif re.search(r"^(獅子|狮子|leo)", msg):
            msg = "leo"
        elif re.search(r"^(處女|处女|virgo)", msg):
            msg = "virgo"
        elif re.search(r"^(天秤|libra)", msg):
            msg = "libra"
        elif re.search(r"^(天蠍|天蝎|scorpio)", msg):
            msg = "scorpio"
        elif re.search(r"^(人馬|射手|sagittarius)", msg):
            msg = "sagittarus"
        elif re.search(r"^(水瓶|aqurius)", msg):
            msg = "aqurius"
        elif re.search(r"^(雙魚|双鱼|pisces)", msg):
            msg = "pisces"
        elif re.search(r"^(牡羊|白羊|aries)", msg):
            msg = "aries"
        else:
            msg = None

        return msg

    def set_dataset(self):
        link = None

        url = "http://www.meiguoshenpo.com/meiri/susanmiller/"
        try:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, "html.parser")
            for div in soup.findAll("div", attrs={"class": "list_item"}):
                for a in div.findAll("a"):
                    link = a["href"]

                break

            if link:
                self.link = link
        except requests.exceptions.ConnectionError:
            print "Fail to link {}".format(url)

        if hasattr(self, "link"):
            self.dataset = [(self.link, self.filename),]
        else:
            self.set_dataset()

    def crawl_job(self):
        self.set_dataset()

        results = {}

        for url, filename in self.dataset:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            title, value = None, None
            for p in soup.findAll("p", attrs={"style": "text-indent: 2em;"}):
                text = p.text.strip().encode(UTF8)
                if text == "（注：本运势为精简版运势）":
                    continue

                if title is None:
                    title = self.mapping(text)
                else:
                    value = Converter('zh-hant').convert(text.decode(UTF8)).encode(UTF8)

                    if len(title) > len(value):
                        title, value = value, title

                    results[title] = value

                    title, value = None, None

        filepath = os.path.join(data_dir(self.repository), self.filename)
        folder = os.path.dirname(filepath)

        if not os.path.exists(folder):
            os.makedirs(folder)
            print "create {} successfully".format(folder)

        with open(filepath, "wb") as out_file:
            json.dump(results, out_file)

        self.gen_results()
        self.insert_answer()

    def gen_results(self):
        filepath = os.path.join(data_dir(self.repository), self.filename)
        with open(filepath, "rb") as in_file:
            self.info = json.load(in_file)

        print "rebuild the info of {} successfully".format(type(self).__name__)

    def bots(self, question):
        answer = None
        msg = self.mapping(question)

        if msg:
            _, rc = self.ask(msg)

            if rc:
                answer = "[{}]的今天星座運勢如下\n{}".format(question, rc.encode(UTF8))

        return answer

bot = LuckyBot()

if __name__ == "__main__":
    bot.crawl_job()

    print bot.bots(sys.argv[1])
