import requests
import jsonfeed as jf
from bottle import Bottle, redirect, request, response, HTTPError

ERROR_MESSAGES = {
    404: "This page could not be resolved."
}

# get wraps requests.get with some basic error handling.
def get(url):
    response = requests.get(url)
    if not response.ok:
        raise HTTPError(
            status=response.status_code,
            body=ERROR_MESSAGES.get(response.status_code)
        )
    return response

# initialize returns a Bottle app to serve the generated JSON feed and its
# favicon.
#
# title: string - the title for this JSON Feed.
# base_url_format: string - the URL format for all pages for which this app will
#   serve feeds.
# response_to_items: (requests.Response) => jf.Item[] - a function that
#   transforms a response from the target site into a list of corresponding
#   jsonfeed items.
# max_items: int - the maximum number of items this feed will serve.
def initialize(title, base_url_format, response_to_items, max_items=20):
    make_url = lambda category: base_url_format.format(category=category)
    # Define primary handler.
    def handle(category=""):
        specific_url = make_url(category)
        res = jf.Feed(
            title=title,
            home_page_url=specific_url,
            feed_url=request.url,
            items=response_to_items(get(specific_url))[:max_items]
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
