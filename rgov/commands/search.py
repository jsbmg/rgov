from cleo import Command
from cleo.helpers import option, argument

from rgov import search


class SearchCommand(Command):

    name = "search"
    description = "Search for campground ids"
    arguments = [argument("terms", "The terms to search for", multiple=True)]
    options = [
        option("descriptions", "d", "Search descriptions"),
        option("interactive", "i", "Interact with the search results")
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
        search_terms = self.argument("terms")
        
        if self.option("descriptions"):
            # target_column determines which column of the csv is
            # searched. '2' is the campsite descriptions and '1' is the
            # campsite names.
            target_column = 2 
        else:
            target_column = 1
            
        search_results = search.search(search_terms, target_column)
        for name, id_num in search_results:
            self.line(f"{name} [<question>{id_num}</>]") 
