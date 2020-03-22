import requests
import jsonfeed as jf
from bottle import Bottle, redirect, request, response, HTTPError

ERROR_MESSAGES = {
    404: "This page could not be resolved."
}

# get wraps requests.get with some basic error handling.
def get(url):
    page = requests.get(url)
    if not page.ok:
        raise HTTPError(
            status=page.status_code,
            body=ERROR_MESSAGES.get(page.status_code)
        )
    return page

# initialize returns a Bottle app to serve the generated JSON feed and its
# favicon.
#
# base_url: string - the root URL for all pages for which this app will serve
#   feeds. Requests for category feeds will simply append the category to this
#   base URL.
# page_to_items: (requests.Response) => jf.Item[] - a function that transforms
#   a response from the target site into a list of corresponding jsonfeed items.
# max_items: int - the maximum number of items this feed will serve.
def initialize(base_url, page_to_items, max_items=20):
    # Avoid double-forward-slases.
    make_url = lambda category: base_url + "/" + category
    if base_url[-1] == "/":
        make_url = lambda category: base_url + category

    # Define primary handler.
    def handle(category=""):
        specific_url = make_url(category)
        res = jf.Feed(
            title="FIXME",
            home_page_url=specific_url,
            feed_url=request.url,
            items=page_to_items(get(specific_url))[:max_items]
        )
        response.content_type = 'application/json'
        return res.toJSON()

    # Construct bottle app.
    bottle = Bottle()
    @bottle.route('/favicon.ico')
    def favicon():
        return redirect(make_url('favicon.ico'))
    @bottle.route('/')
    def serve_root():
        return handle()
    @bottle.route('/<category>')
    def serve_category(category):
        return handle(category=category)
    return bottle;
