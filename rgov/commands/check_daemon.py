import datetime
import getpass
import logging
import time

import daemon

from cleo import Command
from cleo.helpers import option, argument

from rgov.utils import check_command, pushsafer
from rgov.utils.constants import Paths

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
            "notify-limit",
            "N",
            "The number of notifications to send before the program exits [3]",
            flag=False,
            value_required=True,
        ),
        option(
            "command",
            "c",
            "Command to run if availability found",
            flag=False,
            value_required=True,
        ),
    ]

    def handle(self) -> int:
        campground_ids = self.argument("id")

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
            
        if self.option("notify-limit"):
            notify_limit = self.option("notify-limit")
        else:
            notify_limit = 3
            
        request_dates = check_command.get_request_dates(arrival_date, length_of_stay)
        stay_dates = check_command.get_stay_dates(arrival_date, length_of_stay)

        # make sure the api key works
        authenticated = False
        while authenticated == False:
            ps_username, ps_api_key = pushsafer.input_credentials()
            authenticated = pushsafer.validate_key(ps_username, ps_api_key)
            if authenticated == False:
                self.line("Invalid credentials.")

        self.line("<fg=magenta>Daemon started.</fg=magenta>")
        
        with daemon.DaemonContext():
            logging.basicConfig(filename=Paths.log_file,
                                filemode='a',
                                format='[%(asctime)s] %(message)s',
                                datefmt='%Y/%d/%m %H:%M:%S',
                                level=logging.INFO)
            logging.info('starting to search')
            
            notifications_sent = 0
            
            while True:
                logging.info('------------checking------------')
                campgrounds = {}
                found_available = False
                for campground_id in campground_ids:
                    campground_name = check_command.get_campground_name(campground_id)
                    try:
                        data = check_command.request(request_dates, campground_id)
                    except HTTPError as e:
                        logging.error(e)
                        time.sleep(10)
                        continue
                        
                    available_sites = check_command.get_available_sites(data, stay_dates)
                    
                    if available_sites:
                        logging.info(f'{campground_name} - found available site(s)')
                        campgrounds[campground_name] = available_sites
                        found_available = True
                    else:
                        logging.info(f'{campground_name} - no available site(s)')

                    if campground_id != campground_ids[-1]:
                        time.sleep(1)

                if found_available:
                    message = pushsafer.gen_notifier_text(campgrounds)
                    pushsafer_status = pushsafer.notify(ps_api_key, 'a', message)
                    if pushsafer_status['status'] == 0:
                        logging.error(f"Pushsafer: {pushsafer_status}")
                    else:
                        logging.info(f"Pushsafer: {pushsafer_status}")
                    notifications_sent += 1
                    
                if notifications_sent == notify_limit:
                    reached_notify_limit = ("notification limit reached "
                                            f"[{num_anotifications}] - exiting")
                    logging.info(reached_notify_limit)
                    return 0
                                           
                time.sleep(300)  # wait 5 minutes before rechecking


