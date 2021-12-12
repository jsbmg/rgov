import json

from rgov import locations
from rgov.campground import Campground
from tests import gen_sample


DATES = gen_sample.SAMPLE_DATES
CAMPGROUND = gen_sample.SAMPLE_CAMPGROUND


def test_name():
    cg = Campground("232279")
    assert cg.name == "Laguna"


def test_availability():
    CAMPGROUND.get_available(DATES.request_dates, DATES.stay_dates, test=True)
    assert CAMPGROUND.available == [
        "001",
        "002",
        "023",
        "024",
        "030",
        "026",
        "034",
        "043",
        "041",
        "038",
        "037",
        "021",
        "031",
        "027",
        "008",
        "006",
        "017",
        "025",
        "007",
        "039",
        "010",
        "016",
        "003",
        "028",
        "029",
        "020",
        "036",
        "035",
        "004",
        "018",
        "032",
        "042",
        "040",
        "015",
        "005",
        "022",
        "009",
        "033",
    ]
    assert (
        CAMPGROUND.gen_cli_text()
        == "<info>Laguna</>: <fg=magenta>38</> sites available"
    )

    assert (
        CAMPGROUND.url
        == "https://www.recreation.gov/camping/campgrounds/232279/availability"
    )
