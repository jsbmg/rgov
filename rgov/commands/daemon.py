import daemon
import datetime
import time
from subprocess import run, Popen

from cleo import Command
from cleo.helpers import option, argument

from rgov.commands import check_command


class DaemonCommand(check_command.CheckCommand):

    name = "daemon"
    description = "Start a daemon that checks for availablity automatically"

    help = """The <info>daemon</info> command automatically checks campground(s)
availability on the dates of stay every 5 minutes as a background process. Like
the check command, the daemon command defaults to the current date with a three
nights stay. The following example checks for a three night stay starting on
October 12, 2021 at Laguna:

<info>rgov daemon 232279 -date 10-12-2021 -length 3</info>

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
            value_required=True,
        ),
    ]

    def handle(self):
        campground_ids = self.argument("id")

        if self.option("notifier"):
            notifier = self.option("notifier")
        else:
            notifier = "notify-send"

        self.line("<fg=magenta>Rgov daemon started.</fg=magenta>")

        with daemon.DaemonContext():
            while True:
                notify = False
                notification = [notifier, "rgov"]
                results = {}
                for campground_id in campground_ids:
                    try:
                        campground_name, available_sites = self.main(campground_id)
                        results[campground_name] = len(available_sites)
                    except UnboundLocalError:
                        run([notifier,
                             "rgov",
                             f"{campground_id} - invalid id!"])
                        continue
                for campground_name, num_sites in results.items():
                    if num_sites >= 1:
                        line = (f"{campground_name} - "
                                f"{num_sites} site(s) available")
                        notification.append(line)
                        notify = True
                if notify == True:
                    if self.option("notifier"):
                        run(notification)
                    if self.option("command"):
                        command = self.option("command")
                        Popen(command, shell=True)
                    if self.option("forever"):
                        pass
                    else:
                        import sys
                        sys.exit()

                time.sleep(300)  # 5 minutes until next check
