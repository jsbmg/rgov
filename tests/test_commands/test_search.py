from cleo import Application
from cleo import CommandTester
import pytest

from rgov.commands import search

application = Application()
application.add(search.SearchCommand())
command = application.find('search')
tester = CommandTester(command)

def test_lodgepole():
    tester.execute("detroit")
    assert "233258" in tester.io.fetch_output()
