from modules.pages import (
  History,
  Ratings
)

from modules.scraper import Responser
from modules.constants import Config
import json
import sys
import os


# Main entry point of the application
if __name__ == '__main__':

    # Initialize configuration 
    config = Config(sys.argv[1] if len(sys.argv) > 1 else None)

    # Validate username
    if not config.username:
        raise ValueError(f"Please provide a username: python {sys.argv[0]} <username>")

    # Verify username is valid  
    assert Responser(config.USER_PROFILE_URL).is_success, f"Invalid username: {config.username}"

    # Fetch history data
    history = History(
        user_history_url=config.USER_HISTORY_URL,
        # start_date="2023-11-14",
        # end_date= arrow.now().format(USER_DAY_FORMAT)
    )

    history_data = history.data
    history_parsed_data = history.parsed_data
    
    # Process history data
    history_parsed_data_ratings = Ratings.update_ratings(
        config.USER_RATINGS_URL,
        history_parsed_data
        )

    # Create exports directory 
    if not os.path.exists(config.EXPORTS_DIR):
        os.makedirs(config.EXPORTS_DIR)

    # Export history to JSON
    history_path = os.path.join(
        config.EXPORTS_DIR,
        config.username + '-history.json'
        )

    with open(history_path, 'w') as f: 
        json.dump(history_data, f, indent=2)

    # Export context to JSON  
    context_path = os.path.join(
        config.EXPORTS_DIR,
        config.username + '-context.json'
        )

    with open(context_path, 'w') as f: 
        json.dump(history_parsed_data_ratings, f, indent=2)

    print("Done.")