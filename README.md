# jsonfeed-wrapper

`jsonfeed-wrapper` is a Bottle application utility for serving JSON Feeds munged upon request from another site's HTML. It's developed with Google App Engine in mind.


## Installation

```
pip install -r requirements.txt
```

## Usage

The central task is to define a `page_to_items` function that takes `page`, a successful [`requests.Response`](https://requests.readthedocs.io/en/master/api/#requests.Response) for your root URL or some child, and processes it into an array of [`jsonfeed`](https://github.com/lukasschwab/jsonfeed) items.

### `bottle` app

```python
import jsonfeed_wrapper as jfw
import jsonfeed as jf

def page_to_items(page):
  # Implement me!
  # Return a list of jsonfeed items.
  return []

wrapper = jfw.JSONFeedWrapper("https://example.com", page_to_items, 20)
app = wrapper.as_bottle_app()
```

If you're running in Google App Engine or with their `dev_appserver.py` util, just definining `app` is sufficient. Othwerwise, you should additionally call `app.run()` to start the server.

For example, see `bottle-example.py`.

### Cloud Function

```python
import jsonfeed_wrapper as jfw
import jsonfeed as jf

def page_to_items(page):
  # Implement me!
  # Return a list of jsonfeed items.
  return []

wrapper = jfw.JSONFeedWrapper("https://example.com", page_to_items, 20)
target =  wrapper.as_cloud_function()
```

Where `target` is your Cloud Function target, the function invoked each time your Cloud Function receives a request.

For example, see `cloud-function-example.py`.

## Examples

These may be helpful examples for desigining a `page_to_items` function.

+ [`itsnicethat-feed`](https://github.com/lukasschwab/itsnicethat-feed): a generated feed for [It's Nice That](https://www.itsnicethat.com/).

+ [`atlas-feed`](https://github.com/lukasschwab/itsnicethat-feed): a generated feed for [Atlas of Places](https://atlasofplaces.com/).

+ [`bandcamp-feeds`](https://github.com/lukasschwab/bandcamp-feeds): generated feeds for Bandcamp artist profiles.

## To do

+ Refactor `atlas-feed` to use this.
