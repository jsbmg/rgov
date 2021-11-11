import csv
import datetime
import time

from urllib.error import HTTPError

from cleo import Command
from cleo.helpers import option, argument

from rgov.utils import search_command as s_c
from rgov.utils import check_command as c_c

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

        campground_selections = {}
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
                
            search_results = s_c.search(search_input_list, target_column)
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
                        campground_selections[campground] = search_results[campground]
            else: 
                no_results_msg = (f"No results for {search_input}. " 
                                   "Try appending \"-d\".")
                self.line(no_results_msg)

            search_input = self.ask("\nSearch for more campgrounds "
                                    "(or press Enter to continue):")

            
        if not campground_selections:
            self.line("Nothing to do.")
            return 0
        self.line("<info>Your selections</>: ")
        for name in campground_selections.keys():
            self.line(f"* <fg=yellow>{name}</>")
        self.line("")

        ids = campground_selections.values()
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

        length_of_stay = int(self.ask('Enter number of nights:'))
        self.line("")

        arrival_date = f"{month}-{day}-{year}"
        arrival_date_parsed = c_c.parse_arrival_date(arrival_date)
        request_dates = c_c.get_request_dates(arrival_date_parsed,
                                                        length_of_stay)
        stay_dates = c_c.get_stay_dates(arrival_date_parsed, length_of_stay)

        unavailable = []
        col_width = max(map(len, campground_selections))
        self.line("<fg=green>Availability</>:")
        for campground_name, campground_id in campground_selections.items():
            try:
                campground_name, available_sites = c_c.check(campground_id,
                                                             request_dates,
                                                             stay_dates)
            except HTTPError as e:
                error_output = c_c.format_cli_error(campground_name,
                                                    e,
                                                    col_width)
                self.line(error_output)
                time.sleep(2)
                continue

            output = c_c.format_cli_output(campground_name,
                                           available_sites,
                                           col_width)
            self.line(output)
                      
            if not available_sites:
                unavailable.append(campground_id)


        if unavailable:
            self.line("")
            daemon_question = ("One or more campground(s) unavailable. "
                               "Start rgov daemon?")
            if not self.confirm(daemon_question, False):
                return
            else:
                ids = " ".join(unavailable)
                args = ids + f" -d {arrival_date} -l {length_of_stay}"
                self.call('daemon', args)
