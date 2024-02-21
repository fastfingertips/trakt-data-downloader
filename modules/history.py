from .scraper import (
    Responser,
    Element,
    Meta,
)

from .constants import Config
import arrow

def get_history(user_history_url, start_date=None, end_date=None):
    data = {
        'days': {},
    }

    history_dom = Responser(user_history_url).dom
    last_page = int(history_dom.find_all('li', class_='page')[-1].text)
    print('last page: ', last_page)
    current_page = 1
    while True:
        print(f'History Page {current_page}/{last_page}')
        current_dom = Responser(f"{user_history_url}?page={current_page}").dom

        # ITEMS
        items = current_dom.find_all('div', class_='grid-item')
        for item in items:

            # PARSING ITEM DATE
            item_date = item.find('span', class_='format-date')['data-date']
            item_date = arrow.get(item_date).to('local').format(Config.USER_DATE_FORMAT)
            item_day = arrow.get(item_date).format(Config.USER_DAY_FORMAT)

            # PARSING ITEM RATING
            """
            <div class="corner-rating corner-rating-4"><div class="text">4</div></div>
            """

            # ITEM APPEND
            if item_day not in data['days']:
                data['days'][item_day] = []

            data['days'][item_day].append(
                {
                'date': item_date, # ITEM DATE
                **{att: item[att] for att in item.attrs}, # ITEM ATTRIBUTES
                **Meta(item).attrs, # ITEM META ATTRIBUTES
                **Element(item, 'img').attrs, # ITEM IMG ATTRIBUTES
                }
            )

        if start_date is not None and end_date is not None:
            items_dates = data['days'].copy().keys()
            arrange = arrow.Arrow.range('day', arrow.get(start_date), arrow.get(end_date))
            arrange = [date.format(Config.USER_DAY_FORMAT) for date in arrange]
            # arrange = map(lambda x: x.format(day_format), arrange)

            for date in items_dates:
                if date not in arrange:
                    del data['days'][date]

        if current_page == last_page:
            break
        current_page += 1

    return data

def get_first_watched_date(history, item_id, item_type):
    dates = []
    key = f'data-{item_type}-id'
    days = history['days']
    for day in days:
        for item in days[day]:
            if item['data-type'] == item_type and item[key] == item_id:
                dates.append(item['date'])

    return dates[-1] if dates else None

def history_reader(history:dict) -> dict:
    watched_movies = {}
    watched_shows = {}
    watched_episodes = {}
    # counts
    movie_count = 0
    episode_count = 0
    # runtime
    movie_runtime = 0
    episode_runtime = 0

    """
    Some movies, series, or TV show episodes may share the same name.
    Therefore, during storage, we primarily use the ID of the data.
    > data-movie-id
    > data-show-id
    > data-episode-id
    """

    days = history['days']
    for day in days:
        for item in days[day]:
            if item['data-type'] == 'movie':
                if item['data-movie-id'] not in watched_movies:
                    watched_movies[item['data-movie-id']] = {
                        'name': item['meta-name'],
                        'last_watched': item['date'],
                        'first_watched': get_first_watched_date(history, item['data-movie-id'], 'movie'),
                        'count': 1
                    }
                else:
                    watched_movies[item['data-movie-id']]['count'] += 1
                movie_runtime += int(item['data-runtime'])
                movie_count += 1
            elif item['data-type'] == 'episode':
                if item['data-show-id'] not in watched_shows:
                    watched_shows[item['data-show-id']] = {
                        'name': item['meta-name'],
                        'last_watched': item['date'],
                        'first_watched': get_first_watched_date(history, item['data-episode-id'], 'episode'),
                        'count': 1
                    }
                else:
                    watched_shows[item['data-show-id']]['count'] += 1
                if item['data-episode-id'] not in watched_episodes:
                    watched_episodes[item['data-episode-id']] = {
                        'name': item['meta-episode-name'],
                        'count': 1
                    }
                else:
                    watched_episodes[item['data-episode-id']]['count'] += 1
                episode_runtime += int(item['data-runtime'])
                episode_count += 1

    # SORTING
    watched_movies = dict(sorted(watched_movies.items(), key=lambda item: item[1]['count'], reverse=True))
    watched_shows = dict(sorted(watched_shows.items(), key=lambda item: item[1]['count'], reverse=True))
    watched_episodes = dict(sorted(watched_episodes.items(), key=lambda item: item[1]['count'], reverse=True))

    context = {
        'movies': {
            'count': movie_count,
            'unique_count': len(watched_movies),
            'data': watched_movies,
            'runtime': movie_runtime
        },
        'shows': {
            'data': watched_shows,
            'count': len(watched_shows),
            'episodes': {
                'count': episode_count,
                'unique_count': len(watched_episodes),
                'data': watched_episodes,
                'runtime': episode_runtime
                }
        },
        'total': {
            'count': movie_count + episode_count,
            'runtime': movie_runtime + episode_runtime
        },
        'diff': {
            'count': movie_count - episode_count,
            'runtime': movie_runtime - episode_runtime
        }
    }

    return context