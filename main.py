from modules.history import (
    history_reader,
    get_history
)

from modules.ratings import update_ratings
from modules.constants import Config
import json
import sys
import os

if __name__ == '__main__':
    config = Config(sys.argv[1] if len(sys.argv) > 1 else None)

    if not config.USERNAME:
        raise ValueError("Please provide a username: python main.py <username>")

    print(config.USER_HISTORY_URL)
    # data fetch
    history = get_history(
        user_history_url=config.USER_HISTORY_URL,
        # start_date="2023-11-14",
        # end_date= arrow.now().format(USER_DAY_FORMAT)
    )
    context = history_reader(history)
    context = update_ratings(config.USER_RATINGS_URL, context)

    # exports directory
    if not os.path.exists(config.EXPORTS_DIR):
        os.makedirs(config.EXPORTS_DIR)

    # history
    history_path = os.path.join(
        config.EXPORTS_DIR,
        config.USERNAME + '-history.json'
        )

    with open(history_path, 'w') as f: 
        json.dump(history, f, indent=2)

    # context
    context_path = os.path.join(
        config.EXPORTS_DIR,
        config.USERNAME + '-context.json'
        )

    with open(context_path, 'w') as f: 
        json.dump(context, f, indent=2)

    print("Done.")