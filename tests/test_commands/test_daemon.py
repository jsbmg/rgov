from cleo import Application
from cleo import CommandTester
import pytest

from rgov.commands import daemon, check_command

application = Application()
application.add(daemon.DaemonCommand())
command = application.find("daemon")
tester = CommandTester(command)


# def test_laguna():
#     tester.execute("232279")
#     assert "Laguna" in tester.io.fetch_output()
