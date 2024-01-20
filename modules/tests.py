"""def get_today_items():
    items_dict = get_history(USER_HISTORY_URL)
    today = arrow.now().format(USER_DAY_FORMAT)
    if today in items_dict:
        return items_dict[today]
    return []
"""
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