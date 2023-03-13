from collections import defaultdict
from datetime import datetime

import rgov.commands.check


def check_for_combo_availability(dates, per_date_availability):
    dates_dict = defaultdict(dict)
    for campground in per_date_availability.keys():
        for date in per_date_availability[campground].keys():
            dates_dict[date][campground] = per_date_availability[campground][date]
    possible_combo = True
    for date in dates.stay_dates:
        if not dates_dict[date]:
            possible_combo = False
            break
    if possible_combo:
        return dates_dict
    else:
        return None

