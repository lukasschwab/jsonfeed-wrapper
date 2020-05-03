import jsonfeed_wrapper as jfw
import jsonfeed as jf
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt, timedelta

# The old-style base URL is used to calculate item URLs.
BASE_URL = "https://www.itsnicethat.com"
BASE_URL_FORMAT = BASE_URL + "/{category}"
MAX_ITEMS = 20

# Tries to match e.g. '10 hours ago'; otherwise defaults to now.
def marshalItsNiceThatHoursAgo(string_date):
    date_published = dt.utcnow()
    try:
        first_token = string_date.split()[0]
        # Sometimes it's "a day ago."
        hours_ago = 1 if first_token == "a" else int(string_date.split()[0])
        date_published -= timedelta(hours=hours_ago)
    except ValueError:
        print("Defauling to NOW:", string_date)
        pass
    # Messy: just make it UTC by adding the Zulu indicator.
    return date_published.isoformat() + "Z"

# Tries to match e.g. '16 October 2019'; otherwise defers to
# marshalItsNiceThatHoursAgo.
def marshalItsNiceThatDate(string_date):
    try:
        # Messy: just make it UTC by adding the Zulu indicator.
        return dt.strptime(string_date, "%d %B %Y").isoformat() + "Z"
    except ValueError:
        return marshalItsNiceThatHoursAgo(string_date)

def raw_item_to_item(listing):
    url = listing.find('a')['href']
    title = listing.find(class_="listing-item-title").text
    raw_tags = listing.findAll(class_="tag")
    # Ignore the "more tags" ellipsis.
    tags = [tag.text for tag in raw_tags if tag.text != '...']
    date_published = marshalItsNiceThatDate(
        listing.find(class_="first-cap").text
    )
    return jf.Item(
        id=url,
        url=BASE_URL+url,
        title=title,
        tags=tags,
        date_published=date_published,
        content_text=title
    )

def page_to_items(page):
    soup = bs(page.text, 'html.parser')
    raw_items = soup.findAll(class_="listing-item")[:MAX_ITEMS]
    return [raw_item_to_item(s) for s in raw_items]

# app is a Bottle app; in the appengine environment it's run automatically, but
# in this non-appengine example we need to call app.run() ourselves.
app = jfw.initialize("Example Feed", BASE_URL_FORMAT, page_to_items, MAX_ITEMS)
app.run()
