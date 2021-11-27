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

    help = """The <question>search</> command searches a local database for campground id(s). By default, search arguments are matched with the name of the campground, but the <comment>descriptions</> option can be enabled to search for matching descriptions.

The campground index can always be rebuilt or updated via the <question>init</> command.

<options=bold>Examples:</>

Search for all campgrounds associated with the Grand Canyon:

    $ <info>rgov search -d grand canyon</>

Search for the campground "North Rim Campground":

    $ <info>rgov search north rim</>
"""
    
    def handle(self):
        search_terms = self.argument("terms")
        
        if self.option("descriptions"):
            descriptions = True
        else:
            descriptions = False 
            
        search_results = search.search(search_terms, descriptions)

        for name, id_num in search_results:
            self.line(f"<info>{name}</> [<question>{id_num}</>]") 
