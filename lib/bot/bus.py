#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import datetime
import requests
import difflib
import threading

from lib.common.bot import Bot
from lib.common.utils import UTF8, crawl, data_dir

class BusBot(Bot):
    repository = "bus"
    filename = "bus.json"

    def get_ticket(self):
        ticket = None

        try:
            response = requests.get("http://ptx.transportdata.tw/MOTC/v2/Account/Login?UserData.account=javawokr&UserData.password=P%40%24%24w0rdji3g4wu0h96&$format=JSON")
            rc = json.loads(response.content)

            if rc["Status"]:
                ticket = rc["Ticket"]

            self.ticket_timestamp = int(time.time())
        except ValueError as e:
            pass

        return ticket

    def set_ticket(self, retry_count=3):
        self.ticket = None

        while retry_count > 0:
            self.ticket = self.get_ticket()

            if self.ticket is not None:
                print "set the ticket({}) successfully".format(self.ticket)

                break
            else:
                print "retry to get the ticket"

                self.ticket = None

            retry_count -= 1

    def hourly_job(self):
        for url, filename in self.dataset[len(self.dataset)/2:]:
            crawl(url, os.path.join(data_dir(self.repository)), filename, compression=False)

    def set_dataset(self):
        if not hasattr(self, "ticket_timestamp") or int(time.time()) - self.ticket_timestamp > 86400/4:
            self.set_ticket()

        ticket = ""
        if hasattr(self, "ticket"):
            ticket = "ticket={}".format(self.ticket)

        self.dataset = [("http://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Taipei?$top=30000&$format=JSON".format(self.ticket), "time_taipei.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/NewTaipei?$top=30000&$format=JSON".format(self.ticket), "time_newtaipei.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Taoyuan?$top=30000&$format=JSON".format(self.ticket), "time_taoyuan.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Taichung?$top=30000&$format=JSON".format(self.ticket), "time_taichung.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Kaohsiung?$top=30000&$format=JSON".format(self.ticket), "time_kaosiung.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Tainan?$top=30000&$format=JSON".format(self.ticket), "time_tainan.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Taipei?$top=30000&$format=JSON".format(self.ticket), "stop_taipei.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/NewTaipei?$top=30000&$format=JSON".format(self.ticket), "stop_newtaipei.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Taoyuan?$top=30000&$format=JSON".format(self.ticket), "stop_taoyuan.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Taichung?$top=30000&$format=JSON".format(self.ticket), "stop_taichung.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Kaohsiung?$top=30000&$format=JSON".format(self.ticket), "stop_kaosiung.json"),
                        ("http://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Tainan?$top=30000&$format=JSON".format(self.ticket), "stop_tainan.json"),
                       ]

    def crawl_job(self):
        idx = 0
        while idx < len(self.dataset)/2:
            url, filename = self.dataset[idx]

            city = filename.replace(".json", "").split("_")[1]

            crawl(url, self.repository, filename, compression=False)

            is_pass = self.gen_sub_results(city)
            if is_pass:
                idx += 1

    def gen_sub_results(self, target):
        target = target.lower()
        print "start to build the information of {} bus".format(target)

        stop = {}
        filepath = os.path.join(data_dir(self.repository), "stop_{}.json".format(target))
        if not os.path.exists(filepath):
            self.hourly_job()

        with open(filepath, "rb") as in_file:
            for t in json.load(in_file):
                if "RouteUID" in t:
                    route_id = t["RouteUID"]
                    departure_stop = t.get("DepartureStopNameZh", None)
                    destination_stop = t.get("DestinationStopNameZh", None)

                    #if departure_stop and destination_stop:
                    stop[route_id] = (destination_stop, departure_stop)
                    #else:
                    #    print "Not found the needed elements in this JSON on {}".format(filepath)
                else:
                    print "Not found RouteID element of JSON file({})".format(filepath)

        filepath = os.path.join(data_dir(self.repository), "time_{}.json".format(target))
        if not os.path.exists(filepath):
            self.crawl_job()

        with open(filepath, "rb") as in_file:
            for t in json.load(in_file):
                if "status" in t and not t["status"]:
                    print "Not found the 'status' element of JSON file({}) at {}".format(filepath, target)

                    return False

                route_id, route_name = t["RouteUID"], t["RouteName"]["Zh_tw"]
                station_id, station_name = t["StopUID"], t["StopName"]["Zh_tw"]
                plate_num, station_status = t.get("PlateNumb", 1), t.get("StopStatus", 5)

                go_back = t["Direction"]
                estimation_time = t.get("EstimateTime", -1)

                key = "{}{}".format(route_name.encode(UTF8), station_name.encode(UTF8))

                direction, estimation = None, -1
                if station_status in [1, 2, 3, 4] or plate_num == -1 or estimation_time < 0:
                    if station_status == 1:
                        direction = "尚未發車"
                    elif station_status == 2:
                        direction = "交管不停靠"
                    elif station_status == 3:
                        direction = "末班車已過"
                    elif station_status == 4:
                        direction = "今日未營運"
                    else:
                        direction = "查無資料"

                    estimation = -1
                else:
                    direction = "往[{}]方向".format(stop[route_id][go_back].encode(UTF8))
                    estimation = round(((estimation_time) / 60), 1)

                self.info.setdefault(key, {})
                self.info[key][direction] = estimation

        print "rebuild the information of {} bus successfully".format(target)

        self.insert_answer()

        return True

    def gen_results(self, cities=[]):
        for city in cities:
            self.gen_sub_results(city.lower())

        self.insert_answer()

    def bots(self, msg):
        reply_txt = None

        def checking(info, crawling_timestamp):
            r = ""

            for direction, estimation in info:
                adjusted_timestamp = (time.time() - crawling_timestamp)/60

                if estimation > 0:
                    estimation -= adjusted_timestamp
                    estimation = round(estimation, 1)

                    direction = direction.encode(UTF8)
                    if estimation < 1:
                        r += "{} 進站中\n".format(direction)
                    elif estimation > 180:
                        r += "{} 末班車已駛離\n".format(direction)
                    else:
                        r += "{} 預估 {} 分鐘到達\n".format(direction, estimation)

            return r

        crawling_datetime, answer = self.ask(msg)
        if answer:
            reply_txt = msg + "\n"

            reply_txt += checking(answer.items(), time.mktime(crawling_datetime.timetuple()))
        else:
            '''
            candiated, matching = [], None
            max_similarity = -sys.maxint
            ordered_similarity = {}

            for stop_info in self.info.keys():
                if stop_info.startswith(msg):
                    candiated.append(stop_info)

            for stop_info in (candiated if candiated else self.info.keys()):
                similarity = difflib.SequenceMatcher(None, msg, stop_info).ratio()
                if similarity > 0.7:
                    ordered_similarity[stop_info] = similarity

                    if similarity > max_similarity:
                        max_similarity = similarity
                        matching = stop_info

            if matching:
                reply_txt = matching + "\n"

                reply_txt += checking(self.info[matching].items())
            else:
                reply_txt = "查無[{}]此公車資訊，不知是否您是要查詢\n".format(msg)
                for idx, (stop_info, _) in sorted(ordered_similarity.items(), key=lambda e: e[1], reverse=True)[:3]:
                    reply_txt += "{}. [{}]\n".format(idx+1, stop_info)

                reply_txt = None
            '''
            reply_txt = None

        if reply_txt:
            reply_txt = reply_txt.strip().replace("\n\n", "\n")
            if reply_txt == msg:
                    reply_txt += "\n目前查無公車資訊"

        return reply_txt

bot = BusBot()

if __name__ == "__main__":
    bot.crawl_job()

    print bot.bots(sys.argv[1])
