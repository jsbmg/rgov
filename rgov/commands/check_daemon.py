import logging
import os
import time

import daemon

from cleo import Command
from cleo.helpers import argument, option

from rgov import locations, pushsafer
from rgov.campground import Campground
from rgov.dates import Dates
from rgov import utils


class DaemonCommand(Command):
    name = "daemon"
    description = "Start a daemon that checks for availability automatically"

    help = """The <question>daemon</> command starts a Unix daemon that checks for campground availability every five minutes. If one or more campground(s) are found to have available sites, a Pushsafer notification is sent with a summary of which campground(s) are currently available.

Note that a Pushsafer account and API key is required to use this command, and devices (e.g. a phone) must be configured for for it to work.

<options=bold>Examples:</>

Check if North Rim Campground has available sites on February 2nd, 2022 for 3 nights, and quit after four notifications have been sent:

    $ <info>rgov daemon --notify-limit 4 2-2-2022 3 232489</>

Check if North Rim and Spring Canyon campgrounds have available sites on March 20th, 2022 for five nights:

    $ <info>rgov daemon 3-20-2022 5 232489 234064</>
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
        option(
            "any-combo",
            "a",
            "Notify if there is any contiguous availability across different sites",
        ),
        option(
            "priority",
            "p",
            "Set the priority for the notification, between -2 and 2.",
            flag=False,
            value_required=True,
        ),
        option(
            "interval",
            "i",
            "Number of seconds between checking (minimum 30)",
            flag=False,
            value_required=True,
        ),
    ]

    def handle(self) -> int:
        id_input = self.argument("id")
        date_input = self.argument("date")
        length_input = self.argument("length")
        any_combo = self.option("any-combo")

        if self.option("notify-limit"):
            notify_limit = int(self.option("notify-limit"))
        else:
            notify_limit = 3

        if self.option("priority"):
            priority = int(self.option("priority"))

            if priority > 2 or priority < -2:
                self.line("Priority should be between -2 and 2.")
                return 1
        else:
            priority = 0

        if self.option("interval"):
            interval = int(self.option("interval"))

            if (interval) < 30:
                self.line("Interval must be greater than 30.")
                return 1
        else:
            interval = 300  # wait 5 minutes before checking again

        dates = Dates(date_input, length_input)
        campgrounds = [Campground(id) for id in id_input]

        # make sure the api key works
        if os.path.exists(locations.AUTH_FILE):
            ps_username, ps_api_key = pushsafer.read_credentials()
            authenticated = pushsafer.validate_key(ps_username, ps_api_key)
        else:
            authenticated = False

        while not authenticated:
            ps_username, ps_api_key = pushsafer.input_credentials()
            authenticated = pushsafer.validate_key(ps_username, ps_api_key)

            if not authenticated:
                self.line("Invalid credentials.")
            else:
                if self.confirm("Save for future use?", False):
                    pushsafer.write_credentials(ps_username, ps_api_key)

        self.line("<fg=magenta>Starting to check.</fg=magenta>")
        with daemon.DaemonContext():
            logging.basicConfig(
                filename=locations.LOG_FILE,
                filemode="a",
                format="[%(asctime)s] %(message)s",
                datefmt="%Y/%d/%m %H:%M:%S",
                level=logging.INFO,
            )
            logging.info("starting to search")

            notification_counter = 0

            while True:
                logging.info("------------checking------------")

                available = {}
                per_date_availability = {}
                found_available_sites = False
                for campground in campgrounds:
                    try:
                        campground.get_available(dates.request_dates, dates.stay_dates)

                    except Exception as error:
                        logging.error(error)
                        time.sleep(10)
                        continue

                    per_date_availability[campground.name] = (
                        campground.per_date_availability
                    )

                    if len(campground.available) > 0:
                        logging.info(f"{campground.name} - found available site(s)")
                        available[campground.name] = campground.available
                        found_available_sites = True
                    else:
                        logging.info(f"{campground.name} - no available site(s)")

                    if campground != campgrounds[-1]:
                        time.sleep(1)

                if available:
                    message = pushsafer.gen_notifier_text(available)

                    pushsafer_status = pushsafer.notify(
                        ps_api_key, "a", message, critical
                    )

                    if pushsafer_status["status"] == 0:
                        logging.error(f"Pushsafer: {pushsafer_status}")
                    else:
                        logging.info(f"Pushsafer: {pushsafer_status}")

                    notification_counter += 1

                elif any_combo:
                    logging.info(
                        f"Checking for cross-site/cross-campground availability"
                    )

                    dates_dict = utils.check_for_combo_availability(
                        dates, per_date_availability
                    )

                    if dates_dict is not None:
                        logging.info(
                            f"Found availability accross sites. Sending pushsafer notification"
                        )

                        message = pushsafer.gen_any_combo_notifier_text(
                            dates_dict, dates.stay_dates
                        )

                        pushsafer_status = pushsafer.notify(
                            ps_api_key, "a", message, critical
                        )

                        if pushsafer_status["status"] == 0:
                            logging.error(f"Pushsafer: {pushsafer_status}")
                        else:
                            logging.info(f"Pushsafer: {pushsafer_status}")

                        notification_counter += 1

                if notification_counter == notify_limit:
                    reached_notify_limit = (
                        "notification limit reached "
                        f"[{notification_counter}/"
                        f"{notify_limit}] - exiting"
                    )

                    logging.info(reached_notify_limit)

                    return 0

                time.sleep(interval)
