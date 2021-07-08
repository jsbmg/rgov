from cleo.helpers import argument, option

from rgov.commands import check_command

class CheckCommand(check_command.CheckCommand):

    name = "check"
    description = "Check a campground for availability"

    arguments = [
        argument("id", "The campground id(s) to check", multiple=True)
    ]
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

<info>pandcamp check 232279 -date 10-12-2021 -length 3</info>

Campground ids can be found using <info>search</info> command. To check multiple
campgrounds, separate the campground ids with spaces:

<info>pandcamp check 232279 232278</info>

Unless otherwise specified, the command checks for the current date and a
length of stay of three days. The <comment>--url</comment> option prints the
url along with the results for quickly navigating to the reservation web page.

"""

    def handle(self) -> int:
        campground_ids = self.argument("id")

        for campground_id in campground_ids:
            try:
                campground_name, available_sites = self.main(campground_id)
            except UnboundLocalError:
                invalid_id_line = (f"<fg=red> \u2022 <info>{campground_id}</info> "
                                   f"is not a valid campground id</fg=red>")
                self.line(invalid_id_line)
                continue

            num_sites = len(available_sites)

            # if id is valid
            if 1 <= num_sites <= 12:
                sitelist_sorted = sorted(available_sites)
                result_string = " ".join(sitelist_sorted)
            elif num_sites > 12:
                result_string = f"{num_sites} sites available"
            else:
                result_string = "<fg=yellow>No sites available</fg=yellow>"

            result_line = (f"<question> \u2022 {campground_name}</question> - "
                           f"<fg=cyan>{result_string}</fg=cyan>")
            url_line = (f"<fg=green>   "
                        "https://www.recreation.gov/camping/campgrounds/"
                        f"{campground_id}/availability</fg=green>")

            self.line(result_line)
            if self.option("url"):
                self.line(url_line)
