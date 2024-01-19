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
    data = {
        'days': {},
        'types': {}
    }
    dom = doReadPage(user_history_url)
    last_page = int(dom.find_all('li', class_='page')[-1].text)
    print('last page: ', last_page)
    current_page = 1
    while True:
        current_url = f"{user_history_url}?page={current_page}"
        print(f'Page {current_page}/{last_page}')
        current_dom = doReadPage(current_url)
        # ITEMS
        items = current_dom.find_all('div', class_='grid-item')
        for item in items:
            


            meta_attrs = {}
            item_meta_tags = item.find_all('meta')
            for meta in item_meta_tags:
                attrs = meta.attrs
                print(attrs)
                if 'itemprop' in attrs:
                    meta_attrs['meta-' + attrs['itemprop'].lower()] = attrs['content']

            item_name = item.find('meta', itemprop='name')['content']
            item_url = item.find('meta', itemprop='url')['content']

            item_date = item.find('span', class_='format-date')['data-date']
            item_date = arrow.get(item_date).to('local').format(USER_DATE_FORMAT)
            item_day = arrow.get(item_date).format(USER_DAY_FORMAT)

            # Add new item to dict
            if item_day not in data['days']:
                data['days'][item_day] = []

            data['days'][item_day].append({
                'date': item_date
                } | {att: item[att] for att in item.attrs} | meta_attrs
            )
            print(json.dumps(data, indent=2))
        
        if start_date is not None and end_date is not None:
            items_dates = data['days'].copy().keys()
            arrange = arrow.Arrow.range('day', arrow.get(start_date), arrow.get(end_date))
            arrange = [date.format(USER_DAY_FORMAT) for date in arrange]
            # arrange = map(lambda x: x.format(day_format), arrange)

            for date in items_dates:
                if date not in arrange:
                    del data['days'][date]

        if current_page == last_page:
            break
        current_page += 1

    return data


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

def get_name_from_id(id):
    dom = doReadPage(f"{SITE_URL}/movies/{id}")
    name = dom.find('meta', itemprop='name')['content']
    return name

def history_reader(history):
    watched_movies = {}
    watched_shows = {}
    watched_episodes = {}
    movie_count = 0
    movie_runtime = 0
    episode_count = 0
    episode_runtime = 0
    total_runtime = 0

    days = history['days']

    for day in days:
        for item in days[day]:
            if item['data-type'] == 'movie':
                if item['data-movie-id'] not in watched_movies:
                    watched_movies[item['data-movie-id']] = {
                        'name': item['name'],
                        'count': 1
                    }
                watched_movies[item['data-movie-id']]['count'] += 1
                movie_runtime += int(item['data-runtime'])
                movie_count += 1
            elif item['data-type'] == 'episode':
                if item['data-episode-id'] not in watched_episodes:
                    watched_episodes[item['data-episode-id']] = {
                        'name': item['name'],
                        'count': 1
                    }
                watched_episodes[item['data-episode-id']]['count'] += 1
                episode_runtime += int(item['data-runtime'])
                episode_count += 1

    # sort most watched
    watched_movies_sorted = sorted(watched_movies.items(), key=lambda x: x[1]['count'], reverse=True)
    watched_episodes_sorted = sorted(watched_episodes.items(), key=lambda x: x[1]['count'], reverse=True)
    total_runtime = movie_runtime + episode_runtime
    diff_runtime = movie_runtime - episode_runtime

    context = {
        'movie': {
            'count': movie_count,
            'unique_count': watched_movies,
            'runtime': movie_runtime
        },
        'episode': {
            'count': episode_count,
            'unique_count': watched_episodes,
            'runtime': episode_runtime
        },
        'total': {
            'count': movie_count + episode_count,
            'runtime': total_runtime
        },
        'diff': {
            'count': movie_count - episode_count,
            'runtime': diff_runtime
        }
    }

    return context

if __name__ == '__main__':

    history = get_history(
        user_history_url=USER_HISTORY_URL
        # start_date="2023-11-14",
        # end_date= arrow.now().format(USER_DAY_FORMAT)
    )

    context = history_reader(history)
    print(json.dumps(context, indent=4))