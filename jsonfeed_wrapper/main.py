import requests
import jsonfeed as jf
import json
from bottle import Bottle, redirect, request, response, HTTPError


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
            response_to_items,
            max_items=20,
            user_agent="jsonfeed_wrapper"
        ):
        self.title = title
        self.base_url_format = base_url_format
        self.response_to_items = response_to_items
        self.max_items = max_items
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
        items = self.response_to_items(self._get(specific_url))[:self.max_items]
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
