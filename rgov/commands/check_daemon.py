import datetime
import getpass
import time

import daemon

from cleo import Command
from cleo.helpers import option, argument

from rgov.utils import check_command, pushsafer

class DaemonCommand(Command):

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
        option("forever", "f", "Don't exit after finding first available sites"),
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

        if self.option("date"):
            date_input = self.option("date")
            arrival_date = check_command.parse_arrival_date(date_input)
        else:
            arrival_date = datetime.date.today()
            
        if self.option("length"):
            length_input = self.option("length")
            length_of_stay = check_command.parse_length_of_stay(length_input)
        else:
            length_of_stay = 3

        request_dates = check_command.get_request_dates(arrival_date, length_of_stay)
        stay_dates = check_command.get_stay_dates(arrival_date, length_of_stay)

        # make sure the api key works before proceeding
        key_test = 0
        while key_test == 0:
            ps_username, ps_api_key = pushsafer.input_credentials()
            key_test = pushsafer.validate_key(ps_username, ps_api_key)
            if key_test == 0:
                self.line("Invalid credentials.")
                
        self.line("<fg=magenta>Daemon started.</fg=magenta>")
        
        with daemon.DaemonContext():
            while True:
                campgrounds = {}
                for campground_id in campground_ids:
                    campground_name = check_command.get_campground_name(campground_id)
                    data = check_command.request(request_dates, campground_id)
                    available_sites = check_command.get_available_sites(data, stay_dates)
                    if available_sites:
                        campgrounds[campground_name] = available_sites

                notification = ""
                if campgrounds:
                    for campground, sites in campgrounds.items():
                        url = check_command.generate_campground_url(campground_id)
                        num_sites_available = len(sites)
                        if 1 <= num_sites_available <= 12:
                            sorted_sites = ", ".join(sorted(available_sites))
                            text_output = (f"· {campground_name}: "
                                           f"site(s) {sorted_sites} available!")
                            notification += text_output + "\n"
                        elif num_sites_available > 12:
                            text_output = (f"· {campground_name}: "
                                           f"{num_sites_available} sites available!")
                            notification += text_output + "\n"
                            
                    pushsafer.notify(ps_api_key, 'a', url, notification)
                    
                    if not self.option("forever"):
                        return 0
                                           
                time.sleep(300)  # wait 5 minutes before rechecking
