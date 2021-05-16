import requests
import json
from typing import Callable

import feedparser
from bottle import Bottle, redirect, request, response, HTTPError

import jsonfeed as jf
import jsonfeed.converters as jfc


ERROR_MESSAGES = {
    404: "This page could not be resolved."
}

log = lambda request: print(json.dumps(dict(
    severity="INFO",
    message="Serving feed",
    request_url=request.url,
    trace_header=request.headers.get('X-Cloud-Trace-Context')
)))

class JSONFeedWrapper:
    def __init__(
            self,
            title,
            base_url_format,
            response_to_,
            max_=20,
            user_agent="jsonfeed_wrapper"
        ):
        self.title = title
        self.base_url_format = base_url_format
        self.response_to_ = response_to_
        self.max_ = max_
        self.user_agent = user_agent

    def _get(self, url):
        response = requests.get(url, headers={'User-agent': self.user_agent})
        if not response.ok:
            raise HTTPError(
                status=response.status_code,
                body=ERROR_MESSAGES.get(response.status_code)
            )
        return response

    def _make_url(self, category):
        return self.base_url_format.format(category=category)

    # NOTE: trying to default these arguments to the Bubble variables...
    def _feed(self, request_url, category=""):
        specific_url = self._make_url(category)
        items = self.response_to_(self._get(specific_url))[:self.max_]
        return jf.Feed(
            title=self.title,
            home_page_url=specific_url,
            feed_url=request_url,
            items=items,
        ).toJSON()

    def as_bottle_app(self):
        bottle = Bottle()
        @bottle.route('/favicon.ico')
        def favicon():
            return redirect(self._make_url('favicon.ico'))
        @bottle.route('/')
        def serve_root():
            log(request)
            response.content_type = 'application/feed+json'
            return self._feed(request.url)
        @bottle.route('/<category>')
        def serve_category(category):
            log(request)
            response.content_type = 'application/feed+json'
            return self._feed(request.url, category=category)
        return bottle

    def as_cloud_function(self):
        def entry_point(request):
            log(request)
            path = request.path.strip("/")
            if path == "favicon.ico":
                return redirect(self._make_url('favicon.ico'))
            category = path if len(path) > 0 else ""
            feed = self._feed(request.url, category)
            return (feed, 200, {'Content-Type': 'application/feed+json'})
        return entry_point


# TODO: it feels disorganized to have this sit in the same file as
# JSONFeedWrapper; these are substantially different wrappers!
class JSONFeedWrapperFromFeed:
    """
    JSONFeedWrapperFromFeed converts a `feedparser`-parseable feed, then applies
    the specified `item_transform` function. If `item_transform(i)` is `None`,
    the item is dropped from the resulting feed.
    """
    def __init__(
            self,
            feed_url: str,
            item_transform: Callable[[jsonfeed.Item], jsonfeed.Item],
        ):
        self.feed_url = feed_url
        self.item_transform = item_transform

    def _feed(self):
        atom_feed = feedparser.parse(self.feed_url)
        json_feed = jfc.from_feedparser_obj(atom_feed)
        # Apply the transform to each item; filter out None results
        transformed = [self.item_transform(i) for i in json_feed.items]
        json_feed.items = [item for item in transformed if item is not None]
        return json_feed

    def as_cloud_function(self):
        def entry_point(request):
            log(request)
            feed = self._feed()
            return (feed, 200, {'Content-Type': 'application/feed+json'})
        return entry_point
