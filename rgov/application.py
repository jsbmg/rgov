import sys

from cleo import Application
from rgov.commands import check, check_daemon, initialize, run, search

commands = [
    check.CheckCommand(),
    search.SearchCommand(),
    initialize.InitCommand(),
    run.RunCommand(),
    check_daemon.DaemonCommand(),
]

application = Application()

[application.add(command) for command in commands]


def main():
    application.run()


if __name__ == "__main__":
    main()
