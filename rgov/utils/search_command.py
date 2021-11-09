import csv

from typing import Generator

from rgov.utils.constants import Paths


def search(search_terms: str, target_column: int) -> Generator[tuple[str, str], None, None]:
    search_terms_lowercase = [term.lower() for term in search_terms]
    num_search_terms = len(search_terms)
    
    search_results = {}
    try:
        with open(Paths.index_path, "r") as i:
            reader = csv.reader(i)
            try:
                for row in reader:
                    count = 0
                    for term in search_terms_lowercase:
                        if term in row[target_column]:
                            count += 1
                            if count == num_search_terms:
                                yield row[1].title(), row[0]
                                
            except IndexError:
                # occurs when trying to search descriptions but the
                # index wasn't built including them
                raise IndexError('No descriptions in the database. '
                                 'Try "rgov init --with-descriptions".')

    except FileNotFoundError:
        # the database has not been built yet
        raise FileNotFoundError('No campground database. Try "rgov init".')


