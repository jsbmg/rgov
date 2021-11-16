import datetime
import getpass
import logging
import os
import time

import daemon

from cleo import Command
from cleo.helpers import option, argument

from rgov import locations
from rgov import pushsafer
from rgov.campground import Campground
from rgov.dates import Dates


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
        argument("date", "The date of your arrival (mm-dd-yyyy)"),
        argument("length", "The length of stay in nights"),
        argument("id", "The campground id(s) to check", multiple=True),
    ]

    options = [
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
        id_input = self.argument("id")
        date_input = self.argument("date")
        length_input = self.argument("length")
            
        if self.option("notify-limit"):
            notify_limit = int(self.option("notify-limit"))
        else:
            notify_limit = 3
            
        dates = Dates(date_input, length_input)
        campgrounds = [Campground(id) for id in id_input]

        # make sure the api key works
        if os.path.exists(locations.AUTH_FILE):
            ps_username, ps_api_key = pushsafer.read_credentials()
            authenticated = pushsafer.validate_key(ps_username, ps_api_key)
        else:
            authenticated = False
        while authenticated == False:
            ps_username, ps_api_key = pushsafer.input_credentials()
            authenticated = pushsafer.validate_key(ps_username, ps_api_key)
            if authenticated == False:
                self.line("Invalid credentials.")
            else:
                if self.confirm("Save for future use?", False):
                    pushsafer.write_credentials(ps_username, ps_api_key)

        self.line("<fg=magenta>Starting to check.</fg=magenta>")
        with daemon.DaemonContext():
            logging.basicConfig(filename=locations.LOG_FILE,
                                filemode='a',
                                format='[%(asctime)s] %(message)s',
                                datefmt='%Y/%d/%m %H:%M:%S',
                                level=logging.INFO)
            logging.info('starting to search')
            
            notification_counter = 0
            
            while True:
                logging.info('------------checking------------')
                available = {} 
                for campground in campgrounds:
                    try:
                        campground.get_available(dates.request_dates, dates.stay_dates)

                    except (HTTPError, IndexError) as error:
                        logging.error(error)
                        time.sleep(10)
                        continue
                        
                    if len(campground.available) > 0:
                        logging.info(f'{campground.name} - found available site(s)')
                        available[campground.name] = campground.available
                    else:
                        logging.info(f'{campground.name} - no available site(s)')

                    if campground != campgrounds[-1]:
                        time.sleep(1)

                if available:
                    message = pushsafer.gen_notifier_text(available)
                    pushsafer_status = pushsafer.notify(ps_api_key, 'a', message)
                    if pushsafer_status['status'] == 0:
                        logging.error(f"Pushsafer: {pushsafer_status}")
                    else:
                        logging.info(f"Pushsafer: {pushsafer_status}")
                    notification_counter += 1
                if notification_counter == notify_limit:
                    reached_notify_limit = ("notification limit reached "
                                            f"[{notification_counter}/" 
                                            f"{notify_limit}] - exiting")
                    logging.info(reached_notify_limit)
                    return 0
                                           
                time.sleep(300)  # wait 5 minutes before rechecking
