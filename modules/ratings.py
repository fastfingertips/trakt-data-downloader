from .scraper import Responser

def update_ratings(ratings_url:str, context:dict) -> dict:
    """
    Ratıng data types:
    - movie (+)
    - show (+)
    - episode (+)
    - season
    """
    ratings_dom = Responser(ratings_url).dom
    try:
        last_page = int(ratings_dom.find_all('li', class_='page')[-1].text)
        print('last page: ', last_page)
        current_page =1
        while True:
            print(f'Rating Page {current_page}/{last_page}')
            current_dom = Responser(f"{ratings_url}?page={current_page}").dom
            items = current_dom.find_all('div', class_='grid-item')
            # For example, <h4 class="ellipsify"><i class="fa-solid fa-heart grid-trakt-heart rating-4"></i> <b>4</b> — Poor</h4>
            for item in items:
                item_type = item['data-type']
                if item_type == 'episode':
                    item_id = item['data-episode-id']
                elif item_type == 'show':
                    item_id = item['data-show-id']
                elif item_type == 'season':
                    item_id = item['data-season-id']
                else:
                    item_id = item['data-movie-id']

                divs = item.find_all('div')
                for div in divs:
                    for style in div['class']:
                        if 'rating-' in style:
                            rating = int(style.replace('rating-', ''))
                            if item_type == 'movie' or item_type == 'show' or item_type == 'episode':
                                # The rating information with the last ID becomes equal to later IDs.
                                # For example, the last rating given to a section changes, even though the initial rating is different.
                                try:
                                    if item_type == 'movie':
                                        context['movies']['data'][item_id]['rating'] = rating
                                    elif item_type == 'show':
                                        context['shows']['data'][item_id]['rating'] = rating
                                    else: # episode
                                        context['shows']['episodes']['data'][item_id]['rating'] = rating
                                except KeyError:
                                    print(f'Episode rated but not watched: ID: {item_id} Rating: {rating}')
                            else:
                                # print(f'Inappropriate data type was passed. Data type: {item_type}')
                                pass
            if current_page == last_page:
                break
            else:
                current_page += 1
    except IndexError:
            print(f'No ratings found on {ratings_url}')
    return context