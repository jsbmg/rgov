from cleo import Application

from rgov.commands import check, search, reindex, daemon

commands = [
    check.CheckCommand(),
    search.SearchCommand(),
    reindex.UpdateIndexCommand(),
    daemon.DaemonCommand(),
]

application = Application()

[application.add(command) for command in commands]


def main() -> int:
    return application.run()


if __name__ == "__main__":
    run()
