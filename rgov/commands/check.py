from datetime import datetime
from urllib.error import HTTPError

from cleo import Command
from cleo.helpers import argument, option

from rgov import utils
from rgov.campground import Campground
from rgov.dates import Dates


class CheckCommand(Command):
    name = "check"
    description = "Check campground(s) for availability"
    arguments = [
        argument("date", "The date if arrival (mm-dd-yyyy)"),
        argument("length", "Length of stay in nights"),
        argument("id", "The campground id(s) to check", multiple=True),
    ]
    options = [
        option("cron-mode", "c", "Run once and notify if availability found"),
        option("url", "u", "Print the campground url(s) with the output"),
    ]

    help = """The <question>check</> command prints out a summary of campsite availability for the the given campground(s) over the specified date range. 

All three arguments are required, and the campground id(s) must be the final argument. The id(s) can be found using the <question>search</> command or by finding the number that is in the url on the corresponding campground's www.recreation.gov webpage.  

The cron-mode option will send a Pushsafer notification (if set up). It is intended as a replacement for the <question>daemon</> command, if running a daemon is not desirable or the system is not Unix.  

<options=bold>Examples:</>

Check if North Rim Campground has available sites on February 2nd, 2022 for 3 nights:

    $ <info>rgov check 2-2-2022 3 232489</>

Check if North Rim and Spring Canyon campgrounds have available sites on March 20th, 2022 for 4 nights:

    $ <info>rgov check 3-20-2022 4 232489 234064</>
"""

    def handle(self) -> int:
        ids_input = self.argument("id")
        date_input = self.argument("date")
        length_input = self.argument("length")

        campgrounds = [Campground(id) for id in ids_input]
        dates = Dates(date_input, length_input)

        column_width = max([len(c.name) for c in campgrounds])

        per_date_availability = {}
        found_available_sites = False
        for campground in campgrounds:
            try:
                campground.get_available(dates.request_dates, dates.stay_dates)
                if len(campground.available) > 0:
                    found_available_sites = True

            except (HTTPError, IndexError) as error:
                self.line(campground.gen_cli_text(column_width, error))
                continue

            self.line(campground.gen_cli_text(column_width))

            per_date_availability[campground.name] = campground.per_date_availability

        if found_available_sites is False:
            dates_dict = utils.check_for_combo_availability(dates, per_date_availability)

            if dates_dict is not None:
                self.line(" ")
                self.line("No contiguous availability at any one site. However, there are available sites each day of "
                             "your stay:")
                self.line(" ")
                for date in dates.stay_dates:
                    self.line(f"<fg=cyan>{datetime.strptime(date, '%Y-%m-%dT00:00:00Z').strftime('%B %d, %Y')}</>")
                    for campground in dates_dict[date]:
                        output = ", ".join(sorted([str(int(n)) for n in dates_dict[date][campground]]))
                        self.line(f"<fg=magenta>{campground}</>")
                        self.line(output)
                    self.line(" ")

        if self.option("cron-mode"):
            self.line("Not yet implemented.")

        return 0
