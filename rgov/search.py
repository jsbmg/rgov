import sqlite3
from contextlib import closing
from typing import Generator

from rgov import locations


def search(
    terms: list, descriptions=False
) -> Generator[tuple[str, str], None, None]:
    if not isinstance(terms, list):
        raise ValueError("arg: search_terms not a list")

    query = [f"%{term.lower()}%" for term in terms]

    n_terms = len(query)

    if descriptions == True:
        col = "description"
    else:
        col = "name"

    separator = f" AND {col} LIKE "

    sql_qry = f"""SELECT *
               FROM campgrounds
               WHERE ({col} LIKE {separator.join(['?' for _ in query])})
               ORDER BY name;"""

    with closing(sqlite3.connect(locations.FACILITIES_DB)) as con, con, closing(
        con.cursor()
    ) as cur:
        for row in cur.execute(sql_qry, query):
            yield row[1].title(), row[0]
