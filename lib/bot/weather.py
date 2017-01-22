#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json

from google.modules.utils import get_html
from bs4 import BeautifulSoup

from lib.common.bot import Bot
from lib.common.utils import UTF8, crawl, data_dir

class WeatherBot(Bot):
    repository = "weather"
    filename = "weather.json"

    def mapping(self, msg):
        msg = msg.lower()

        if re.search(r"^(桃園|tao)", msg):
            msg = "taoyuan_city"
        elif re.search(r"^(基隆|kee)", msg):
            msg = "keelung_city"
        elif re.search(r"^(台北|臺北|taipei)", msg):
            msg = "taipei_city"
        elif re.search(r"^(新北|new_tai|new taipei city)", msg):
            msg = "new_taipei_city"
        elif re.search(r"^(新竹市|hsinchu_city)", msg):
            msg = "hsinchu_city"
        elif re.search(r"^(新竹縣|hsinchu)", msg):
            msg = "hsinchu_county"
        elif re.search(r"^(苗栗|miao)", msg):
            msg = "miaoli_county"
        elif re.search(r"^(台中|臺中|taichung)", msg):
            msg = "taichung_city"
        elif re.search(r"^(彰化|chang)", msg):
            msg = "changhua_county"
        elif re.search(r"^(南投|nan)", msg):
            msg = "naotou_county"
        elif re.search(r"^(雲林|yun)", msg):
            msg = "yunlin_county"
        elif re.search(r"^(嘉義市|chiayi_city)", msg):
            msg = "chiayi_city"
        elif re.search(r"^(嘉義縣|chiayi)", msg):
            msg = "chiayi_county"
        elif re.search(r"^(宜蘭|yilan)", msg):
            msg = "yilan_county"
        elif re.search(r"^(花蓮|hua)", msg):
            msg = "hualien_county"
        elif re.search(r"^(台東|臺東|taitung)", msg):
            msg = "taitung_county"
        elif re.search(r"^(台南|臺南|tainan)", msg):
            msg = "tainan_city"
        elif re.search(r"^(高雄|kao)", msg):
            msg = "kaohsiung_city"
        elif re.search(r"^(屏東|pin)", msg):
            msg = "pingtung_county"
        elif re.search(r"^(連江|lie)", msg):
            msg = "lienchiang_county"
        elif re.search(r"^(金門|kin)", msg):
            msg = "kinmen_county"
        elif re.search(r"^(澎湖|pen)", msg):
            msg = "penghu_county"
        else:
            msg = None

        return msg

    def set_dataset(self):
        self.dataset = [("http://www.cwb.gov.tw/V7/forecast/taiwan/Taoyuan_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Keelung_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Taipei_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/New_Taipei_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Hsinchu_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Hsinchu_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Miaoli_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Taichung_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Changhua_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Nantou_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Yunlin_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Chiayi_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Chiayi_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Yilan_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Hualien_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Taitung_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Tainan_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Kaohsiung_City.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Pingtung_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Lienchiang_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Kinmen_County.htm", WeatherBot.filename),
                        ("http://www.cwb.gov.tw/V7/forecast/taiwan/Penghu_County.htm", WeatherBot.filename),]

    def crawl_job(self):
        results = {}

        for url, filename in self.dataset:
            city = url.split("/")[-1].replace(".htm", "").lower()
            results.setdefault(city, [[], [], []])

            html = get_html(url)
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.findAll("table", attrs={"class": "FcstBoxTable01"})
            for table in tables:
                for tbody in table.findAll("tbody"):
                    for idx, e in enumerate(tbody):
                        for text in e.text.split("\n"):
                            if text:
                                if len(results[city][idx]) == 1:
                                    text = "溫度: {}°C".format(text.encode("UTF8"))
                                elif len(results[city][idx]) == 2:
                                    text = "體感: {}".format(text.encode("UTF8"))
                                elif len(results[city][idx]) == 3:
                                    text = "降雨機率: {}".format(text.encode("UTF8"))

                                results[city][idx].append(text)

                break

        filepath = os.path.join(data_dir(WeatherBot.repository), WeatherBot.filename)
        folder = os.path.dirname(filepath)

        if not os.path.exists(folder):
            os.makedirs(folder)
            print "create {} successfully".format(folder)

        with open(filepath, "wb") as out_file:
            json.dump(results, out_file)

        self.gen_results()
        self.insert_answer()

    def gen_results(self):
        filepath = os.path.join(data_dir(WeatherBot.repository), WeatherBot.filename)
        with open(filepath, "rb") as in_file:
            self.info = json.load(in_file)

        print "rebuild the info of WeatherBot successfully"

    def bots(self, question):
        results = None

        msg = self.mapping(question)
        if msg:
            _, rc = self.ask(msg)
            if rc:
                results = "\n".join([_ for e in rc for _ in e])

        answer = None
        if results:
            answer = "[{}]的天氣狀況如下\n{}".format(question, results.encode(UTF8))

        return answer

bot = WeatherBot()

if __name__ == "__main__":
    bot = WeatherBot()

    print bot.bots(sys.argv[1])
