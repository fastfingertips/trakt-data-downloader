from bs4 import BeautifulSoup
import requests
import arrow
import json

# -- Local --

from constants import (
    SITE_URL,
    USERNAME,
    USER_PROFILE_URL,
    USER_HISTORY_URL,
    USER_DAY_FORMAT,
    USER_DATE_FORMAT
)

def doReadPage(_url) -> BeautifulSoup:
    """
    Reads and retrieves the DOM of the specified page URL.
    """
    try:
        while True:
            #> https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(_url, timeout=30)
                urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
                if urlDom is not None:
                    return urlDom # Returns the page DOM
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to the Internet. Technical details are provided below.")
                print(str(e))
                continue
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                continue
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                continue
            except KeyboardInterrupt:
                print("Someone closed the program")
            except Exception as e:
                print('Error:', e)
    except Exception as e:
        print('Error:', e)

def get_history(user_history_url, start_date=None, end_date=None):
    dom = doReadPage(user_history_url)

    # ITEMS
    items = dom.find_all('div', class_='grid-item')
    items_dict = {}
    for item in items:
        item_runtime = item['data-runtime']
        item_type = item['data-type']
        item_name = item.find('meta', itemprop='name')['content']
        item_url = item.find('meta', itemprop='url')['content']
        item_date = item.find('span', class_='format-date')['data-date']
        item_date = arrow.get(item_date).to('local').format(USER_DATE_FORMAT)

        item_day = arrow.get(item_date).format(USER_DAY_FORMAT)
        if item_day not in items_dict:
            items_dict[item_day] = []
        
        items_dict[item_day].append({
            'name': item_name,
            'url': item_url,
            'runtime': item_runtime,
            'type': item_type,
            'date': item_date
        })

    if start_date is not None and end_date is not None:
        items_dates = items_dict.copy().keys()
        arrange = arrow.Arrow.range('day', arrow.get(start_date), arrow.get(end_date))
        arrange = [date.format(USER_DAY_FORMAT) for date in arrange]
        # arrange = map(lambda x: x.format(day_format), arrange)

        for date in items_dates:
            if date not in arrange:
                del items_dict[date]

    print(json.dumps(items_dict, indent=4))
    return items_dict

def get_today_items():
    items_dict = get_history(USER_HISTORY_URL)
    today = arrow.now().format(USER_DAY_FORMAT)
    if today in items_dict:
        return items_dict[today]
    return []

"""
def get_today_and_yesterday_items():
    items_dict = get_history(USER_HISTORY_URL)
    today = arrow.now().format(day_format)
    yesterday = arrow.now().shift(days=-1).format(day_format)
    if today in items_dict:
        today_items = items_dict[today]
    else:
        today_items = []
    if yesterday in items_dict:
        yesterday_items = items_dict[yesterday]
    else:
        yesterday_items = []
    return today_items + yesterday_items
"""

def calculate_runtime(history):
    movie_runtime = 0
    episode_runtime = 0
    diff_runtime = 0
    total_runtime = 0
    for date in history:
        for item in history[date]:
            if item['type'] == 'movie':
                movie_runtime += int(item['runtime'])
            elif item['type'] == 'episode':
                episode_runtime += int(item['runtime'])
            total_runtime += int(item['runtime'])
    diff_runtime = movie_runtime - episode_runtime
    return {'movie': movie_runtime, 'episode': episode_runtime, 'total': total_runtime, 'diff': diff_runtime}

if __name__ == '__main__':

    history_items = get_history(
        user_history_url=USER_HISTORY_URL,
        start_date="2023-11-14",
        end_date= arrow.now().format(USER_DAY_FORMAT)
    )

    history_runtime = calculate_runtime(history_items)

    print(json.dumps(history_runtime, indent=4))