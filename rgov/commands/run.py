import csv
import datetime
import time

from urllib.error import HTTPError

from cleo.helpers import option, argument
from cleo import Command

from rgov.campground import Campground
from rgov.dates import Dates
from rgov.search import search 

class RunCommand(Command):

    name = "run"
    description = "Run interactively"

    help = """
The <info>run</> command provides a method to select and and check campgrounds
for availability interactively. It is run with no arguments or options.

A selection list is built by searching for and selecting campgrounds
by name. If <comment>-d</> is appended to the search, campgrounds will be
matched by their descriptions. For example, a search for <comment>san diego
-d</> returns all campgrounds that have the words "san" and "diego"
in their descriptions, but a search for <comment>laguna</> without <comment>-d</> is
more specific because it only searches for names that match "laguna."
"""

    def handle(self):

        campgrounds = [] 
        campground_names = []
        column_width = 0
        search_input = self.ask("Search for campgrounds:")
        while search_input is not None:
            search_input_list = search_input.split(" ")
            # make name search default but if "-d" is appended then
            # search descriptions
            if search_input_list[-1] == "-d":
                target_column = 2 # search descriptions
                del search_input_list[-1] # but don't search for "-d"
            else:
                target_column = 1 # search names
                
            search_results = search(search_input_list, target_column)
            search_results = {name: num for name, num in search_results}
            if search_results:
                # note this requires orderded dicts new in python 3.7
                search_results["(none of the above)"] = None 
                search_input = self.choice('Select campground(s)',
                                           list(search_results.keys()),
                                           multiple=True)
                for campground in search_input:
                    # provides a way to continue without selecting any
                    # of the search results
                    if campground == "(none of the above)":
                        pass
                    else:
                        id_num = search_results[campground]
                        campgrounds.append(Campground(id_num))
                        campground_names.append(campground)
                        len_name = len(campground)
                        if column_width < len_name:
                            column_width = len_name
            else: 
                no_results_msg = (f"No results for {search_input}. " 
                                   "Try appending \"-d\".")
                self.line(no_results_msg)

            search_input = self.ask("\nSearch for more campgrounds "
                                    "(or press Enter to continue):")

        if not campgrounds:
            self.line("Nothing to do.")
            return 0
        self.line("<info>Your selections</>: ")
        for campground in campground_names:
            self.line(f"* <fg=yellow>{campground}</>")
        self.line("")

        def month_validator(num):
            if int(num) not in range(1,13):
                raise Exception("Not a digit from 1-12.")
            return num

        def day_validator(num):
            if int(num) not in range(1,31):
                raise Exception("Not a digit from 1-31.")
            return num

        def year_validator(num):
            this_year = datetime.datetime.today().year
            if int(num) not in range(this_year, this_year + 1):
                raise Exception("Not a valid four digit year.")
            return num

        month = self.create_question('Enter month of arrival:')
        month.set_validator(month_validator)
        month = self.ask(month)

        day = self.create_question('Enter day of arrival:')
        day.set_validator(day_validator)
        day = self.ask(day)

        year = self.create_question('Enter year of arrival:')
        year.set_validator(year_validator)
        year = self.ask(year)

        length_input = self.ask('Enter number of nights:')
        self.line("")

        date_input = f"{month}-{day}-{year}"

        dates = Dates(date_input, length_input)
        unavailable = []

        self.line("<fg=green>Availability</>:")

        for campground in campgrounds:
            try:
                campground.get_available(dates.request_dates, dates.stay_dates)

            except (HTTPError, IndexError) as error:
                self.line(campgorund.gen_cli_text(column_width, error)) 
                time.sleep(2)
                continue

            self.line(campground.gen_cli_text(column_width))
                      
            if len(campground.available) == 0:
                unavailable.append(campground.id_num)

        if unavailable:
            self.line("")
            daemon_question = ("One or more campground(s) unavailable. "
                               "Start rgov daemon?")

            if not self.confirm(daemon_question, False):
                return
            else:
                ids = " ".join(unavailable)
                args = f"{date_input} {length_input} {ids}"
                self.call('daemon', args)
