#!/usr/bin/env python

import threading

from apscheduler.schedulers.blocking import BlockingScheduler
from lib.bot import fxrate, weather, lucky, bus

sched = None
def crawl():
    global sched

    if sched is None:
        fxrate.bot.init()
        weather.bot.init()
        lucky.bot.init()
        bus.bot.init()
        bus.bot.hourly_job()

        sched = BlockingScheduler()

        sched.add_job(weather.bot.crawl_job, "cron", minute="*/15")
        sched.add_job(fxrate.bot.crawl_job, "cron", minute="*")
        sched.add_job(lucky.bot.crawl_job, "cron", hour="*")

        sched.add_job(bus.bot.hourly_job, "cron", hour="*/6")
        sched.add_job(bus.bot.crawl_job, "cron", second="5,35")

        sched.start()

        print "the crawling server is started..."
    else:
        print "the crawling server is already running"

def init():
    thread = threading.Thread(target=crawl)
    thread.start()
