from rgov.campground import Campground

def test_campgrounds():
    cg_1 = Campground("232279")
    assert cg_1.name == "Laguna"
