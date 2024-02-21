from enum import Enum

class DateFormat(Enum):
    DAY = "YYYY-MM-DD"  
    DATETIME = f"{DAY} HH:mm:ss"

class Config:
    SITE_URL = "https://trakt.tv"
    USER_PROFILE_PATTERN = f"{SITE_URL}/users/{{username}}"
    USER_RATINGS_PATTERN = f"{USER_PROFILE_PATTERN}/ratings"
    USER_HISTORY_PATTERN = f"{USER_PROFILE_PATTERN}/history"
    USER_DAY_FORMAT = DateFormat.DAY.value
    USER_DATE_FORMAT = DateFormat.DATETIME.value
    EXPORTS_DIR = 'exports'

    def __init__(self, username):
        self.username = username
        self.set_user_urls(username)

    def set_user_urls(self, username: str):
        self.USER_PROFILE_URL = self.USER_PROFILE_PATTERN.format(username=username)
        self.USER_RATINGS_URL = self.USER_RATINGS_PATTERN.format(username=username)
        self.USER_HISTORY_URL = self.USER_HISTORY_PATTERN.format(username=username)