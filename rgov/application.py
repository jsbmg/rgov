import sys

from cleo import Application

from rgov.commands import check, search, reindex, check_daemon

commands = [
    check.CheckCommand(),
    search.SearchCommand(),
    reindex.UpdateIndexCommand(),
    initialize.InitCommand(),
    check_daemon.DaemonCommand(),
]

application = Application()

[application.add(command) for command in commands]

def main():
    application.run()

if __name__ == "__main__":
    main()
