from cleo import Application
from cleo import CommandTester
import pytest

from rgov.commands import check

application = Application()
application.add(check.CheckCommand())
command = application.find("check")
tester = CommandTester(command)


# def test_laguna():
#     tester.execute("232279")
#     assert "Laguna" in tester.io.fetch_output()

# def test_lodgepole():
#     tester.execute("232461")
#     assert "Lodgepole" in tester.io.fetch_output()

# def test_url():
#     url = "https://www.recreation.gov/camping/campgrounds/232471/availability"
#     tester.execute("232471 -u")
#     assert url in tester.io.fetch_output()

# def test_length():
#     tester.execute("231885 -l 80")
#     assert "Lewis Canyon" in tester.io.fetch_output()
