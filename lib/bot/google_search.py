# -*- coding: utf-8 -*-

import sys

from bs4 import BeautifulSoup
from urllib import urlencode

from google import google, modules
from google.modules.utils import get_html
from google.modules.standard_search import GoogleResult
from google.modules.standard_search import _get_name, _get_link, _get_google_link, _get_description,  _get_thumb,  _get_cached
from googleapiclient.discovery import build

from lib.common.utils import UTF8
from lib.common.bot import Bot

def get_search_url(query, page=0, per_page=10, lang='en', cr=""):
    # note: num per page might not be supported by google anymore (because of
    # google instant)

    params = {'nl': lang, 'q': query.encode('utf8'), 'start': page * per_page, 'num': per_page, 'cr': cr}
    params = urlencode(params)
    url = u"http://www.google.com/search?" + params
    # return u"http://www.google.com/search?hl=%s&q=%s&start=%i&num=%i" %
    # (lang, normalize_query(query), page * per_page, per_page)
    return url

def search(query, pages=1, lang='en', void=True, cr=""):
    """Returns a list of GoogleResult.
    Args:
        query: String to search in google.
        pages: Number of pages where results must be taken.
    Returns:
        A GoogleResult object."""

    results = []
    for i in range(pages):
        url = get_search_url(query, i, lang=lang, cr=cr)
        html = get_html(url)

        if html:
            soup = BeautifulSoup(html, "html.parser")
            divs = soup.findAll("div", attrs={"class": "g"})

            j = 0
            for li in divs:
                res = GoogleResult()

                res.page = i
                res.index = j

                res.name = _get_name(li)
                res.link = _get_link(li)
                res.google_link = _get_google_link(li)
                res.description = _get_description(li)
                res.thumb = _get_thumb()
                res.cached = _get_cached(li)
                if void is True:
                    if res.description is None:
                        continue
                results.append(res)
                j += 1

    return results

modules.utils._get_search_url = get_search_url
google.search = search

def bots_customer_search(msg):
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build("customsearch", "v1", developerKey="AIzaSyBmq0-MkYRKeS0Ay6qNHItwAWLpiPUO0ZM")

    res = service.cse().list(q=msg, cx='017576662512468239146:omuauf_lfve',).execute()

class SearchBot(Bot):
    def set_dataset(self):
        pass

    def crawl_job(self, is_gen=True):
        pass

    def gen_results(self):
        pass

    def bots(self, msg):
        link = None

        search_results = google.search(msg.decode("UTF8"), 1, cr="countryTW")
        for results in search_results:
            link = results.link

            break

        answer = "我不清楚你的問題[{}]，所以提供 google search 結果\n{}".format(msg, link)

        return answer

bot = SearchBot()

if __name__ == "__main__":
    bot = SearchBot()

    print bot.bots(sys.argv[1])
