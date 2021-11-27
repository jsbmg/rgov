import csv

from typing import Generator

from rgov import locations

def search(search_terms: list, target_column: int) -> Generator[tuple[str, str], None, None]:
    if not isinstance(search_terms, list):
         raise ValueError("arg: search_terms not a list")
    search_terms_lowercase = [term.lower() for term in search_terms]
    num_search_terms = len(search_terms)
    try:
        with open(locations.INDEX_PATH, "r") as i:
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


