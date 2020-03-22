import requests
import jsonfeed as jf
from bottle import route, request, response, run, HTTPError

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

class JSONFeedWrapper:
    def __init__(self, base_url, page_to_items, max_items, favicon=None):
        self.base_url = base_url
        self.page_to_items = page_to_items
        self.max_items = max_items
        self.favicon = favicon

    def handle(self, category=""):
        specific_url = self.base_url + "/" + category
        res = jf.Feed(
            title="FIXME",
            home_page_url=specific_url,
            feed_url=request.url,
            items=self.page_to_items(get(specific_url))[:self.max_items]
        )
        response.content_type = 'application/json'
        return res.toJSON()

    def serve(self):
        @route('/')
        def entry():
            return self.handle()

        @route('/<category>')
        def subset(category):
            return self.handle(category=category)

        run(host='localhost', port=8080, debug=True)
