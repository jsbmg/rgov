import datetime
import time

from urllib.error import HTTPError

from cleo import Command
from cleo.helpers import argument, option

from rgov import pushsafer
from rgov.dates import Dates
from rgov.campground import Campground

class CheckCommand(Command):
    name = "check"
    description = "Check campground(s) for availability"
    arguments = [
        argument("date",
                 "The date if arrival (mm-dd-yyyy)"),
        argument("length",
                 "Length of stay in nights"),
        argument("id",
                 "The campground id(s) to check",
                 multiple=True),
    ]
    options = [
        option("cron-mode", "c", "Run once and notify if availability found"),
        option("url", "u", "Print the campground url(s) with the output"),
    ]


    help = """The <info>check</info> command checks campground(s) for availability on the
dates of stay and prints the results to the terminal. The following example
checks for a three night stay starting on October 12, 2021 at Laguna:

<info>rgov check 232279 -date 10-12-2021 -length 3</info>

Campground ids can be found using <info>search</info> command. To check multiple
campgrounds, separate the campground ids with spaces:

<info>rgov check 232279 232278</info>

Unless otherwise specified, the command checks for the current date and a
length of stay of three days. The <comment>--url</comment> option prints the
url along with the results for quickly navigating to the reservation web page.

"""
    
    def handle(self) -> int:
        ids_input = self.argument("id")
        date_input = self.argument("date")
        length_input = self.argument("length")

        campgrounds = [Campground(id) for id in ids_input]
        dates = Dates(date_input, length_input)

        column_width = max([len(c.name) for c in campgrounds])

        for campground in campgrounds:
            try:
                campground.get_available(dates.request_dates, dates.stay_dates)

            except (HTTPError, IndexError) as error:
                self.error(campground.gen_cli_text(column_width, error))
                continue

            self.line(campground.gen_cli_text(column_width))
                
        if self.option("cron-mode"):
            self.line("Not yet implemented.")                

        return 0       

