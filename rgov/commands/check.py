import datetime

from cleo import Command
from cleo.helpers import argument, option

from rgov.utils import constants, check_command


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

        for campground_id in campground_ids:
            campground_name = check_command.get_campground_name(campground_id)
            data = check_command.request(request_dates, campground_id)
            available_sites = check_command.get_available_sites(data, stay_dates)
            num_sites_available = len(available_sites)
            
            if 1 <= num_sites_available <= 12:
                sorted_sites = ", ".join(sorted(available_sites))
                text_output = f"{campground_name}: site(s) {sorted_sites} available!"
            elif num_sites_available > 12:
                text_output = f"{campground_name}: {num_sites_available} sites available!"
            else:
                text_output = f"{campground_name}: No sites available."
                
            if self.option("url"):
                url = check_command.generate_campground_url(campground_id)
                text_output += "\n" + url
                
            self.line(text_output)
                
        return 0
