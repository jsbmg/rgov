import csv

from cleo import Command
from cleo.helpers import option, argument

from rgov.utils import constants


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

<info>rgov reindex --with-descriptions</info>.
"""

    def handle(self):
        """Search campground names and descriptions and print their name and id."""
        search_terms = self.argument("terms")
        search_terms_lowercase = [term.lower() for term in search_terms]
        num_search_terms = len(search_terms)
        
        if self.option("descriptions"):
            # target_column determines which column of the csv is
            # searched. '2' is the campsite descriptions and '1' is the
            # campsite names.
            target_column = 2 
        else:
            target_column = 1
            
        with open(constants.index_path, "r") as i:
            reader = csv.reader(i)
            try:
                for row in reader:
                    count = 0
                    for term in search_terms_lowercase:
                        if term in row[target_column]:
                            count += 1
                            if count == num_search_terms:
                                self.line(
                                    f"<question>{row[1].title()}</question>"
                                    f" - <info>{row[0]}</info>"
                                )
            
            except IndexError:
                # Alert that this error is happening because the
                # descriptions aren't included in the database. They can
                # be included via the --with-descriptions option in the
                # reindex command.
                error_text = (
                    "<fg=red>Description searches "
                    "are disabled.</fg=red>\nEnable with "
                    "<info>rgov reindex --with-descriptions</info>."
                )
                self.line(error_text)
