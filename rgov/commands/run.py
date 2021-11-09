import csv
import datetime
import time

from cleo import Command
from cleo.helpers import option, argument

from rgov.utils import constants, search_command, check_command


class RunCommand(Command):

    name = "run"
    description = "Run interactively"
    options = [
        option("descriptions", "d", "Search descriptions")
        ]

    help = """"""
    
    def handle(self):
        if self.option("descriptions"):
            # target_column determines which column of the csv is
            # searched. '2' is the campsite descriptions and '1' is the
            # campsite names.
            target_column = 2 
        else:
            target_column = 1

        search_results = {}
        selected_campgrounds = []
        query = self.ask("Search for campgrounds:")
        while query is not None:
            # TODO make this understandable
            query_list = query.split(" ")
            if query_list[-1] == "-d":
                target_column = 2
                del query_list[-1]
            else:
                target_column = 1
                
            additional_results = search_command.search(query_list, target_column)
            additional_results = {k: v for k, v in additional_results}
            search_results.update(additional_results)
            new_names = [name for name in additional_results.keys()]
            if not new_names:
                self.line(f"No results for {query}.")
            else:
                new_names.append("(none of the above)")
                query = self.choice('Select campground(s)',
                                    new_names,
                                    multiple=True)
                for campground in query:
                    # it would be better to just hit enter to skip a
                    # choice query but that would require modifying the
                    # cleo source code
                    if campground == "(none of the above)":
                        pass
                    else:
                        selected_campgrounds.append(campground)
            query = self.ask("\nSearch for more campgrounds "
                             "(or press Enter to continue):")
        if not selected_campgrounds:
            self.line("Nothing to do.")
            return 0
        self.line("<info>Your selections</>: ")
        for name in selected_campgrounds:
            self.line(f"· <fg=yellow>{name}</>")
        self.line("")

        ids = [search_results[name] for name in selected_campgrounds]

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
        arrival_date_parsed = check_command.parse_arrival_date(arrival_date)
        request_dates = check_command.get_request_dates(arrival_date_parsed,
                                                        length_of_stay)
        stay_dates = check_command.get_stay_dates(arrival_date_parsed, length_of_stay)

        self.line("<fg=green>Checking</>:")
        unavailable = []
        for campground_id in ids:
            try:
                campground_name, available_sites = check_command.check(campground_id,
                                                                       request_dates,
                                                                       stay_dates)
            except Exception as e:
                self.line(e)
                time.sleep(2)
                continue

            text_output = check_command.generate_cli_output(campground_name,
                                                             available_sites)
            self.line(text_output)
            
            if not available_sites:
                unavailable.append(campground_id)
                
        if unavailable:
            self.line("")
            daemon_question = ("One or more campground(s) are unavailable. "
                               "Start daemon?")
            if not self.confirm(daemon_question, False):
                return
            else:
                ids = " ".join(unavailable)
                args = ids + f" -d {arrival_date} -l {length_of_stay}"
                self.call('daemon', args)
