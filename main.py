from modules.history import (
    history_reader,
    get_history
)


from modules.constants import (
    USER_RATINGS_URL,
    USER_HISTORY_URL
)

from modules.ratings import update_ratings
import json

if __name__ == '__main__':

    history = get_history(
        user_history_url=USER_HISTORY_URL
        # start_date="2023-11-14",
        # end_date= arrow.now().format(USER_DAY_FORMAT)
    )

    context = history_reader(history)
    context = update_ratings(USER_RATINGS_URL, context)

    with open('history.json', 'w') as f:
        json.dump(history, f, indent=2)

    with open('context.json', 'w') as f:
        json.dump(context, f, indent=2)