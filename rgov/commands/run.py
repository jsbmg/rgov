import datetime
import time
from urllib.error import HTTPError

from cleo import Command
from rgov.campground import Campground
from rgov.dates import Dates
from rgov.search import search


class RunCommand(Command):
    def add(self):
        """Interactive prompt to search for and select campgrounds.
        Returns a dictionary of campgrounds, empty if no selections made.
        """
        parks = {}
        user_input = self.ask("Search for campgrounds:")
        if not user_input:
            return parks

        # If the last search term is '-d', search for the terms
        # in the campground descriptions
        words = user_input.split(" ")
        if words[-1] == "-d":
            descriptions = True
            del words[-1]
        else:
            descriptions = False

        # List of matching campgrounds
        results = {name: num for name, num in search(words,descriptions)}

        if results:
            # Select campgrounds from the results list
            results["(none of the above)"] = ""
            user_input = self.choice(
                "Select campground(s)",
                list(results.keys()),
                multiple=True
            )
            for cg in user_input:
                if cg == "(none of the above)":
                    pass
                else:
                    # Add valid selection
                    parks[cg] = Campground(results[cg])

        else:
            msg = f"No results for {user_input}. " 'Try appending "-d".'
            self.line(msg)

        return parks

    def none_selected(self, campgrounds: dict):
        if not campgrounds:
            self.line("Nothing to do.")
            return True
        else:
            return False

    def display_selected(self, campgrounds):
        self.line("\n<fg=yellow>Currently selected</>:")
        for campground in campgrounds:
            self.line(f"<info>{campground}</>")

    name = "run"
    description = "Run interactively"

    help = """The <question>run</> command is an interactive alternative to the <question>search</>, <question>check</>, and <question>daemon</> commands.

Searching for campgrounds and setting the dates are done via prompt. If any or all of the selected campgrounds are unavailable, a confirmation prompt will ask if the <question>daemon</> should be started, which will check for availability every five minutes and send a notification via Pushsafer if availability is found (a Pushsafer account an API key is required for this).

When searching for campgrounds interactively, note that a "-d" appended to the search terms will check for matching campground descriptions, whereas the default is to search for campgrounds by name (more information on description vs. name searches can be found in the help section for the <question>search</> command).
"""

    def handle(self):
        cgs = self.add()

        if not cgs:
            cgs = self.add()

        if self.none_selected(cgs):
            return 0

        self.display_selected(cgs)

        choice = self.ask("\nWhat now? ([a]dd [r]emove [c]ontinue):")

        while choice != "c":
            if choice == "a":
                new = self.add()
                cgs.update(new)

            elif choice == "r":
                to_remove= self.choice(
                    "Select a campground(s) to remove:",
                    list(cgs.keys()),
                    multiple=True,
                )
                for x in to_remove:
                    del cgs[x]

            self.display_selected(cgs)
            choice = self.ask("\nWhat now? (a)dd (r)emove (c)ontinue?")

        if self.none_selected(cgs):
            return 0

        self.line("")
        column_width = max(map(len, cgs))

        def month_validator(num):
            if int(num) not in range(1, 13):
                raise Exception("Not a digit from 1-12.")
            return num

        def day_validator(num):
            if int(num) not in range(1, 31):
                raise Exception("Not a digit from 1-31.")
            return num

        def year_validator(num):
            this_year = datetime.datetime.today().year
            if int(num) not in range(this_year, this_year + 2):
                raise Exception("Not a valid four digit year.")
            return num

        month = self.create_question("Enter month of arrival:")
        month.set_validator(month_validator)
        month = self.ask(month)

        day = self.create_question("Enter day of arrival:")
        day.set_validator(day_validator)
        day = self.ask(day)

        year = self.create_question("Enter year of arrival:")
        year.set_validator(year_validator)
        year = self.ask(year)

        length_input = self.ask("Enter number of nights:")
        self.line("")

        date_input = f"{month}-{day}-{year}"

        dates = Dates(date_input, length_input)
        unavailable = []

        self.line("<fg=yellow>Availability</>:")

        for campground in cgs.values():
            try:
                campground.get_available(dates.request_dates, dates.stay_dates)

            except (HTTPError, IndexError) as error:
                unavailable.append(campground.id_num)
                self.line(campground.gen_cli_text(column_width, error))
                time.sleep(2)
                continue

            self.line(campground.gen_cli_text(column_width))

            if len(campground.available) == 0:
                unavailable.append(campground.id_num)

        if unavailable:
            self.line("")
            daemon_question = (
                "One or more campground(s) unavailable. " "Start rgov daemon?"
            )

            if not self.confirm(daemon_question, False):
                return
            else:
                ids = " ".join(unavailable)
                args = f"{date_input} {length_input} {ids}"
                self.call("daemon", args)
