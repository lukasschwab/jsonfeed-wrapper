import requests
import jsonfeed as jf
from bottle import Bottle, redirect, request, response, HTTPError

ERROR_MESSAGES = {
    404: "This page could not be resolved."
}

def get(url):
    page = requests.get(url)
    if not page.ok:
        raise HTTPError(
            status=page.status_code,
            body=ERROR_MESSAGES.get(page.status_code)
        )
    return page

# class JSONFeedWrapper:
#     def __init__(self, bottle, base_url, page_to_items, max_items):
#         self.base_url = base_url
#         self.page_to_items = page_to_items
#         self.max_items = max_items
#         @bottle.route('/favicon.ico')
#         def favicon():
#             return redirect(self.base_url + '/favicon.ico')
#         @bottle.route('/')
#         def entry():
#             return self.handle()
#         @bottle.route('/<category>')
#         def subset(category):
#             return self.handle(category=category)
#
#     def handle(self, category=""):
#         specific_url = self.base_url + "/" + category
#         res = jf.Feed(
#             title="FIXME",
#             home_page_url=specific_url,
#             feed_url=request.url,
#             items=self.page_to_items(get(specific_url))[:self.max_items]
#         )
#         response.content_type = 'application/json'
#         return res.toJSON()

def initialize(base_url, page_to_items, max_items):
    def handle(category=""):
        specific_url = base_url + "/" + category
        res = jf.Feed(
            title="FIXME",
            home_page_url=specific_url,
            feed_url=request.url,
            items=page_to_items(get(specific_url))[:max_items]
        )
        response.content_type = 'application/json'
        return res.toJSON()
    bottle = Bottle()
    @bottle.route('/favicon.ico')
    def favicon():
        return redirect(base_url + '/favicon.ico')
    @bottle.route('/')
    def serve_root():
        return handle()
    @bottle.route('/<category>')
    def serve_category(category):
        return handle(category=category)
    return bottle;
