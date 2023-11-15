from bs4 import BeautifulSoup
import requests
import arrow
import json

username = ""
profile_url = f"https://trakt.tv/users/{username}"
history_url = profile_url + "/history"
day_format = "YYYY-MM-DD"
date_format = "YYYY-MM-DD HH:mm:ss"

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
                if urlDom != None:
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

def get_history(start_date=None, end_date=None):
    dom = doReadPage(history_url)

    # ITEMS
    items = dom.find_all('div', class_='grid-item')
    items_dict = {}
    for item in items:
        item_runtime = item['data-runtime']
        item_type = item['data-type']
        item_name = item.find('meta', itemprop='name')['content']
        item_url = item.find('meta', itemprop='url')['content']
        item_date = item.find('span', class_='format-date')['data-date']
        item_date = arrow.get(item_date).to('local').format(date_format)

        item_day = arrow.get(item_date).format(day_format)
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
        items = []

        for date in arrow.Arrow.range('day', arrow.get(start_date), arrow.get(end_date)):
            date = date.format(day_format)
            if date in items_dict:
                items += items_dict[date]
        print(json.dumps(items, indent=4))
        return items

    return items_dict

def get_today_items():
    items_dict = get_history()
    today = arrow.now().format(day_format)
    if today in items_dict:
        return items_dict[today]
    return []

"""
def get_today_and_yesterday_items():
    items_dict = get_history()
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

def calculate_runtime(items):
    movie_runtime = 0
    episode_runtime = 0
    diff_runtime = 0
    total_runtime = 0
    for item in items:
        if item['type'] == 'movie':
            movie_runtime += int(item['runtime'])
        elif item['type'] == 'episode':
            episode_runtime += int(item['runtime'])

        total_runtime += int(item['runtime'])
    diff_runtime = movie_runtime - episode_runtime
    return {'movie': movie_runtime, 'episode': episode_runtime, 'total': total_runtime, 'diff': diff_runtime}


if __name__ == '__main__':

    history_items = get_history(
        start_date="2023-11-14",
        end_date= arrow.now().format(day_format)
    )

    history_runtime = calculate_runtime(history_items)

    print(json.dumps(history_runtime, indent=4))