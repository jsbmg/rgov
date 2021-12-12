import json

from rgov import locations
from rgov.campground import Campground
from rgov.dates import Dates

SAMPLE_DATES = Dates("01-29-2022", "10")
SAMPLE_CAMPGROUND = Campground("232279")


def main():
    requests = campground._request(dates.request_dates, dates.stay_dates)

    with open(locations.EXAMPLE_DATA, "w") as f:
        f.write(json.dumps(requests))


if __name__ == "__main__":
    main()
