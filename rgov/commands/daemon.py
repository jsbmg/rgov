import daemon
import datetime
import time
from subprocess import run, Popen

from cleo import Command
from cleo.helpers import option, argument

from rgov.commands import check_command

# TODO add logging for errors and to show that the daemon is running
# TODO add to or better the notification method(s) (e.g. signal, email, twitter, phone, etc)
# TODO show in notifications all campgrounds with availability, not just one or something vague

class DaemonCommand(check_command.CheckCommand):

    name = "daemon"
    description = "Start a daemon that checks for availablity automatically"

    help = """The <info>daemon</info> command automatically checks campground(s)
availability on the dates of stay every 5 minutes as a background process. Like
the check command, the daemon command defaults to the current date with a three
nights stay. The following example checks for a three night stay starting on
October 12, 2021 at Laguna:

<info>pandcamp daemon 232279 -date 10-12-2021 -length 3</info>

Campground ids can be found using the <info>search</info> command.

The <comment>command</comment> option runs a given shell command in the event
one or more of the campgrounds checked are found to have available sites. This
can be used, for example, to send an email with msmtp.

The <comment>--notifier</comment> option specifies a notification program to be
used (e.g. herbe or notify-send) to send a system notification. The notifier
assumes that the format of the notification program is <comment><notification
program> "notification text"</comment>.

Be default, the daemon exits if availability is found, to avoid excess
notifications. This can be disabled with the <comment>--forever</comment>
option.

"""

    arguments = [
        argument("id", "The campground id(s) to check", multiple=True),
    ]

    options = [
        option(
            "length",
            "l",
            "Length of stay in nights [3 nights]",
            flag=False,
            value_required=True,
        ),
        option("forever", "f", "Continue to run even after finding open sites"),
        option(
            "date",
            "d",
            "The date of your arrival, in mm-dd-yyyy format [today]",
            flag=False,
            value_required=True,
        ),
        option(
            "notifier",
            "N",
            "The notifier to run if an availability is found [notify-send]",
            flag=False,
            value_required=True,
        ),
        option(
            "command",
            "c",
            "The command to run if an availability is found",
            flag=False,
            value_required=True),
    ]

    def handle(self):
        campground_ids = self.argument("id")

        if self.option("notifier"):
            notifier = self.option("notifier")
        else:
            notifier = "notify-send"

        self.line("<fg=magenta>Pandcamp daemon started.</fg=magenta>")

        with daemon.DaemonContext():
            while True:
                for campground_id in campground_ids:
                    try:
                        campground_name, available_sites = self.main(campground_id)
                    except UnboundLocalError:
                        run([notifier, "Pandcamp", f"{campground_id} - invalid id!"])
                        continue
                    if len(available_sites) >= 1:
                        if self.option("notifier"):
                            run([notifier, f"{campground_name} - sites found!"])
                        if self.option("command"):
                            command = self.option("command")
                            Popen(command, shell=True)
                        if self.option("forever"):
                            pass

                time.sleep(300)
