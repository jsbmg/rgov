import datetime
import time

from urllib.error import HTTPError

from cleo import Command
from cleo.helpers import argument, option

from rgov.utils import pushsafer
from rgov.utils import check_command as c_c


class CheckCommand(Command):
    name = "check"
    description = "Check a campground for availability"
    arguments = [argument("id",
                          "The campground id(s) to check",
                          multiple=True)]
    options = [
        option(
            "length",
            "l",
            "Length of stay in nights [3 nights]",
            flag=False,
            value_required=True,
        ),
        option("url", "u", "Display the campground url(s)"),
        option(
            "date",
            "d",
            "The date of your arrival, in mm-dd-yyy format [today]",
            flag=False,
            value_required=True,
        ),
        option("chron-mode", "c", "Run once and notifiy if sites available"),
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
    
    def handle(self) ->int:
        campground_ids = self.argument("id")
        
        if self.option("date"):
            date_input = self.option("date")
            arrival_date = c_c.parse_arrival_date(date_input)
        else:
            arrival_date = datetime.date.today()
            
        if self.option("length"):
            length_input = self.option("length")
            length_of_stay = c_c.parse_length_of_stay(length_input)
        else:
            length_of_stay = 3

        request_dates = c_c.get_request_dates(arrival_date, length_of_stay)
        stay_dates = c_c.get_stay_dates(arrival_date, length_of_stay)

        campground_results = {}
        results_table = []
        width = max([len(c_c.get_campground_name(i)) for i in campground_ids])
        for campground_id in campground_ids:
            campground_name = c_c.get_campground_name(campground_id)
            
            try:
                data = c_c.request(request_dates, campground_id)
            except HTTPError as e:
                error_output = c_c.format_error_output(campground_name,
                                                       e,
                                                       width)
                self.line(error_output)
                continue
            
            available_sites = c_c.get_available_sites(data, stay_dates)
            
            if self.option("chron-mode"):
                campground_results[campground_name] = available_sites
            else:
                output = c_c.generate_cli_output(campground_name,
                                                 available_sites,
                                                 width)
                self.line(output)
                
        if self.option("chron-mode"):
            message = pushsafer.gen_message(campground_results)
            if message:
                # TODO get api key without prompting
                # pushsafer.notify(key, 'a', message)
                print("Not yet implemented")
                
        return 0       
