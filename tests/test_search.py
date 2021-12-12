import pytest
from rgov.search import search


def test_search():
    with pytest.raises(ValueError):
        for x in search("laguna", 1):
            pass
    for x in search(["laguna"], descriptions=False):
        assert x == ("Laguna", "232279")
    dt_search = []
    for x in search(["Detroit"], descriptions=True):
        dt_search.append(x)

    assert dt_search == [
        ("Breitenbush Campground", "233301"),
        ("Cove Creek", "233694"),
        ("Fox Creek Group Camp", "233209"),
        ("Hoover Campground", "233693"),
        ("Humbug Campground", "251713"),
        ("Olallie Lake Guard Station Cabin", "233305"),
        ("Riverside At Detroit (Willamette National Forest, Or)", "233258"),
        ("Santiam Flats Campground", "251616"),
        ("Southshore At Detroit Lake", "255135"),
        ("Whispering Falls Campground", "251470"),
    ]
    dt_uncaps_search = []
    for x in search(["detroit"], descriptions=True):
        dt_uncaps_search.append(x)
    assert dt_uncaps_search == [
        ("Breitenbush Campground", "233301"),
        ("Cove Creek", "233694"),
        ("Fox Creek Group Camp", "233209"),
        ("Hoover Campground", "233693"),
        ("Humbug Campground", "251713"),
        ("Olallie Lake Guard Station Cabin", "233305"),
        ("Riverside At Detroit (Willamette National Forest, Or)", "233258"),
        ("Santiam Flats Campground", "251616"),
        ("Southshore At Detroit Lake", "255135"),
        ("Whispering Falls Campground", "251470"),
    ]
