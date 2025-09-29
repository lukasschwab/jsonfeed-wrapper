from typing import Callable, List
import requests
import jsonfeed as jf
import json
from bottle import Bottle, redirect, request, response, HTTPError


ERROR_MESSAGES = {
    404: "This page could not be resolved."
}


def log_request(request):
    print(json.dumps(dict(
        severity="INFO",
        message="Serving feed",
        request_url=request.url,
        trace_header=request.headers.get('X-Cloud-Trace-Context')
    )))


class JSONFeedWrapper:
    def __init__(
            self,
            title: str,
            base_url_format: str,
            response_to_items: Callable[[requests.Response], List[jf.Item]],
            max_items: int = 20,
            user_agent: str = "jsonfeed_wrapper"
        ):
        self.title = title
        self.base_url_format = base_url_format
        self.response_to_items = response_to_items
        self.max_items = max_items
        self.user_agent = user_agent


    def _get(self, url: str) -> requests.Response:
        print(json.dumps(dict(
            severity="INFO",
            message="Requesting upstream URL",
            url=url,
        )))
        response = requests.get(url, headers={'User-agent': self.user_agent})
        if not response.ok:
            print(json.dumps(dict(
                severity="ERROR",
                message="Failed fetching upstream URL: non-OK status",
                status=response.status_code,
                text=response.text,
            )))
            raise HTTPError(
                status=response.status_code,
                body=ERROR_MESSAGES.get(response.status_code)
            )
        return response


    def _make_url(self, category: str) -> str:
        return self.base_url_format.format(category=category)


    # NOTE: trying to default these arguments to the Bubble variables...
    def _feed(self, request_url: str, category: str = "") -> str:
        specific_url = self._make_url(category)
        items = self.response_to_items(self._get(specific_url))[:self.max_items]
        return jf.Feed(
            title=self.title,
            home_page_url=specific_url,
            feed_url=request_url,
            items=items,
        ).to_json()


    def as_bottle_app(self) -> Bottle:
        bottle = Bottle()
        @bottle.route('/favicon.ico')
        def favicon():
            return redirect(self._make_url('favicon.ico'))
        @bottle.route('/')
        def serve_root():
            log_request(request)
            response.content_type = 'application/feed+json'
            return self._feed(request.url)
        @bottle.route('/<category>')
        def serve_category(category):
            log_request(request)
            response.content_type = 'application/feed+json'
            return self._feed(request.url, category=category)
        return bottle

    def as_cloud_function(self) -> Callable:
        def entry_point(request):
            log_request(request)
            path = request.path.strip("/")
            if path == "favicon.ico":
                return redirect(self._make_url('favicon.ico'))
            category = path if len(path) > 0 else ""
            feed = self._feed(request.url, category)
            return (feed, 200, {'Content-Type': 'application/feed+json'})
        return entry_point
