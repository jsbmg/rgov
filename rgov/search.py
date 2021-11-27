import sqlite3

from contextlib import closing
from typing import Generator

from rgov import locations

def search(search_terms: list, 
           descriptions=False) -> Generator[tuple[str, str], None, None]:
    if not isinstance(search_terms, list):
         raise ValueError("arg: search_terms not a list")

    query = [f"%{term.lower()}%" for term in search_terms]

    num_search_terms = len(query)

    if descriptions == True:
        column = 'description'
    else:
        column = 'name'

    separator = f" AND {column} LIKE "

    sql_statement = f"""SELECT *
                     FROM campgrounds 
                     WHERE ({column} LIKE {separator.join(['?' for _ in query])}) 
                     ORDER BY name;"""

    with closing(sqlite3.connect(locations.FACILITIES_DB)) as con, con, \
            closing(con.cursor()) as cur:
        for row in cur.execute(sql_statement, query):
            yield row[1].title(), row[0]
