class Config:
    SITE_URL = "https://trakt.tv"
    USER_DAY_FORMAT = "YYYY-MM-DD"
    USER_DATE_FORMAT = f'{USER_DAY_FORMAT} HH:mm:ss'
    EXPORTS_DIR = 'exports'

    def __init__(self, username):
        self.USERNAME = username
        self.update_user_urls()

    def update_user_urls(self):
        self.USER_PROFILE_URL = f"{self.SITE_URL}/users/{self.USERNAME}"
        self.USER_RATINGS_URL = f"{self.USER_PROFILE_URL}/ratings"
        self.USER_HISTORY_URL = f'{self.USER_PROFILE_URL}/history'