# SITE
SITE_URL = "https://trakt.tv"

# USER
USERNAME = ""
USER_PROFILE_URL = f"{SITE_URL}/users/{USERNAME}"
USER_RATINGS_URL = f"{USER_PROFILE_URL}/ratings"
USER_HISTORY_URL = F'{USER_PROFILE_URL}/history'
USER_DAY_FORMAT = "YYYY-MM-DD"
USER_DATE_FORMAT = f'{USER_DAY_FORMAT} HH:mm:ss'

if not USERNAME:
  raise ValueError("Set your username in constants.py")