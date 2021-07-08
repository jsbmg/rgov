import csv

from cleo import Command
from cleo.helpers import option, argument

from rgov.commands import paths


class SearchCommand(Command):

    name = "search"
    description = "Search for campground ids"
    arguments = [argument("terms", "The terms to search for", multiple=True)]
    options = [
        option("descriptions", "d", "Search descriptions"),
    ]

    help = """The <info>search</info> command searches text to find campground
ids. Multiple search terms can be separated by spaces, to search in an
orderless fashion, or in quotes, to search for exact matches.

By default, the keywords are matched against campground names. The<comment>
--descriptions </comment>option searches against campground descriptions, but
this options requires that the search index be rebuilt (see the
<info>reindex</info> command). This can be done with:

<info>pandcamp reindex --with-descriptions</info>.
"""

    def handle(self):
        """Search campground names and descriptions and print their name and id."""
        search_terms = self.argument("terms")
        search_terms_lowercase = [term.lower() for term in search_terms]
        num_search_terms = len(search_terms)

        # Read the index csv file line by line. If a match is found, the
        # corresponding name and id is printed. If multiple search words, all
        # must match the search string, in any order. The target_column
        # variable specifies which column to search in. Column 1 is names, and
        # column 2 contains the descriptions.
        if self.option("descriptions"):
            target_column = 2  # the search target column
        else:
            target_column = 1
        with open(paths.index_path, "r") as i:
            reader = csv.reader(i)
            try:
                for row in reader:
                    count = 0
                    for term in search_terms_lowercase:
                        if term in row[target_column]:
                            count += 1
                            if count == num_search_terms:
                                self.line(f"<question>{row[1].title()}</question>"
                                          f" - <info>{row[0]}</info>")

            # This error occurs when description option is passed but the csv
            # isn't built with the descriptions included.
            except IndexError:
                error_string = ("<fg=red>Description searches "
                                "are disabled.</fg=red>\nEnable with "
                                "<info>pandcamp reindex --with-descriptions</info>.")
                self.line(error_string)
