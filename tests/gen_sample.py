import json

from rgov import locations
from rgov.campground import Campground
from rgov.dates import Dates

SAMPLE_DATES = Dates("01-29-2022", "10")
SAMPLE_CAMPGROUND = Campground("232279")


def main():
    requests = SAMPLE_CAMPGROUND._request(
        SAMPLE_DATES.request_dates, SAMPLE_DATES.stay_dates
    )

    with open(locations.EXAMPLE_DATA, "w") as f:
        f.write(json.dumps(requests, indent=4))


if __name__ == "__main__":
    main()
