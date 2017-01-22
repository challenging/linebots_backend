#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import pandas as pd

from lib.common.utils import crawl, data_dir
from lib.common.bot import Bot

class RateBot(Bot):
    repository = "fxrate"
    filename = "rate.csv"

    def set_dataset(self):
        self.dataset = [("http://rate.bot.com.tw/xrt/flcsv/0/day", RateBot.filename)]

    def mapping(self, msg):
        msg = msg.upper()

        if msg in ["美金", "美元", "USD"]:
            msg = "USD"
        elif msg in ["港幣", "HKD"]:
            msg = "HKD"
        elif msg in ["英鎊", "GBP"]:
            msg = "GBP"
        elif msg in ["澳幣", "AUD"]:
            msg = "AUD"
        elif msg in ["加拿大幣", "CAD"]:
            msg = "CAD"
        elif msg in ["新加坡幣", "SGD"]:
            msg = "SGD"
        elif msg in ["法朗", "CHF"]:
            msg = "CHF"
        elif msg in ["日圓", "日元", "日幣", "JPY"]:
            msg = "JPY"
        elif msg in ["南非幣", "ZAR"]:
            msg = "ZAR"
        elif msg in ["瑞典幣", "SEK"]:
            msg = "SEK"
        elif msg in ["紐西蘭幣", "NZD"]:
            msg = "NZD"
        elif msg in ["泰銖", "THB"]:
            msg = "THB"
        elif msg in ["比索", "PHP"]:
            msg = "PHP"
        elif msg in ["印尼幣", "印尼盾", "IDR"]:
            msg = "IDR"
        elif msg in ["歐元", "EUR"]:
            msg = "EUR"
        elif msg in ["韓元", "KRW"]:
            msg = "KRW"
        elif msg in ["越南盾", "VND"]:
            msg = "VND"
        elif msg in ["馬來幣", "馬幣", "MYR"]:
            msg = "MYR"
        elif msg in ["人民幣", "CHY"]:
            msg = "CNY"
        else:
            msg = None

        return msg

    def gen_results(self):
        filepath = os.path.join(data_dir(RateBot.repository), RateBot.filename)
        if os.path.exists("{}.gz".format(filepath)):
            os.rename("{}.gz".format(filepath), filepath)

        df = pd.read_csv(filepath, index_col=False)
        for value in df.values:
            currency, buy_cash, buy_spot, sell_cash, sell_spot = value[0], value[2], value[3], value[12], value[13]
            self.info.setdefault(currency, (buy_cash, buy_spot, sell_cash, sell_spot))

        print "rebuild fxrate_info successfully"

    def crawl_job(self):
        for url, filename in self.dataset:
            crawl(url, RateBot.repository, filename)

        self.gen_results()
        self.insert_answer()

    def bots(self, question):
        reply_txt = None
        msg = self.mapping(question)

        if msg:
            _, answer = self.ask(msg)

            if answer:
                reply_txt = "臺灣銀行關於[{}] - 現金賣出({}),即期賣出({});現金買入({}),即期買入({})".format(\
                    question, answer[2], answer[3], answer[0], answer[1])

        return reply_txt

bot = RateBot()

if __name__ == "__main__":
    bot = RateBot()

    print bot.bots(sys.argv[1])
