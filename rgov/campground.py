import contextlib
import json
import sqlite3
from collections import defaultdict
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fake_useragent import UserAgent
from rgov import locations


class AvailabilityNotFoundError(Exception):
    def __init__(self, arg=None):
        if arg:
            self.message = arg
        else:
            self.message = (
                "Try initializing this attribute "
                "with the get_availability() method first."
            )

    def __str__(self):
        return self.message


class Campground:
    def __init__(self, id_num):
        self.id_num = id_num
        self._name = None
        self._available = None
        self._url = None
        self._cli_text = None

    def _request(self, request_dates: list, stay_dates: list) -> list:
        endpoint = "https://www.recreation.gov/api/camps/availability/campground"
        requests = []
        for date in request_dates:
            url = f"{endpoint}/{self.id_num}/month?"
            params = {"start_date": date}
            query_string = urlencode(params)
            url = url + query_string
            request = Request(url)
            request.add_header("User-Agent", UserAgent().random)
            try:
                data = urlopen(request)
            except HTTPError:
                raise
            data = data.read()
            data_loaded = json.loads(data)
            try:
                campsite_data = data_loaded["campsites"]
            except KeyError:
                raise
            requests.append(campsite_data)
        return requests

    def get_available(self, request_dates: list, stay_dates: list, test=False):
        if test:
            requests = []
            with open(locations.EXAMPLE_DATA, "r") as f:
                f = f.read()
                requests = json.loads(f)
        else:
            try:
                requests = self._request(request_dates, stay_dates)
            except (HTTPError, KeyError):
                raise

        d = defaultdict(int)
        for request in requests:
            for site in request.values():
                for date in stay_dates:
                    if date in site["availabilities"]:
                        if site["availabilities"][date] == "Available":
                            d[site["site"]] += 1

        self._available = [k for k, v in d.items() if v == len(stay_dates)]

    @property
    def name(self):
        if not self._name == None:
            return self._name
        else:
            sql_statement = """SELECT name FROM campgrounds WHERE id = (?)"""
            try:
                with contextlib.closing(
                    sqlite3.connect(locations.FACILITIES_DB)
                ) as con, con, contextlib.closing(con.cursor()) as cur:
                    cur.execute(sql_statement, (self.id_num,))
                    self._name = cur.fetchone()[0].title()
                    if not self._name:
                        raise ValueError(f"{self.id_num} is not a valid id.")
                    return self._name
            except sqlite.OperationalError:
                raise sqlite3.OperationalError(
                    (
                        "Something went wrong "
                        "with the database: "
                        "Try running `rgov init`."
                    )
                )

    @property
    def available(self):
        if not self._available == None:
            return self._available
        else:
            raise AvailabilityNotFoundError

    @property
    def url(self):
        if not self._url == None:
            return self._url
        else:
            base_url = "https://www.recreation.gov/camping/campgrounds"
            self._url = f"{base_url}/{self.id_num}/availability"
            return self._url

    def gen_cli_text(self, width=None, error=None):
        col_1 = f"<info>{self.name}</>:"
        len_name = len(self.name)

        if not width:
            width = len_name

        width += len(col_1) - len_name

        if error:
            col_2 = f"<error>{error}</>"
        else:
            try:
                num_available_sites = len(self.available)
            except AvailabilityNotFoundError:
                raise

            if 1 <= num_available_sites <= 12:
                sorted_sites = ", ".join(self.available)
                col_2 = f"<fg=cyan>{sorted_sites}</> available"

            elif num_available_sites > 12:
                col_2 = f"<fg=magenta>{num_available_sites}</> sites available"

            else:
                col_2 = f"<fg=red>full</>"

        self._cli_text = f"{col_1:{width}} {col_2}"
        return self._cli_text
