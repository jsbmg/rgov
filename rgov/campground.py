import csv
import json

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
            self.message = ("Try initializing this attribute"  
                            "with the get_availability() method first.")
    def __str__(self):
        return self.message


class Campground:

    def __init__(self, id_num): 
        self.id_num = id_num
        self._name = None 
        self._available = None 
        self._url = None
        self._cli_text = None

    def get_available(self, request_dates: list, stay_dates: list):
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
            requests.append(campsite_data.values())
           
        available_sites = []
        last_day = stay_dates[-1]
        for request in requests:
            for site in request:
                for date in stay_dates:
                    if date in site["availabilities"]:
                        if site["availabilities"][date] not in "Available":
                            break
                        else:
                            if date == last_day:
                                available_sites.append(site["site"])
        self._available = sorted(available_sites)

    @property
    def name(self):
        if not self._name == None:
            return self._name
        else:
            try:
                with open(locations.INDEX_PATH, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if self.id_num in row[0]:
                            self._name = row[1].title()
                            return self._name 
            except FileNotFoundError:
                error_msg = "Campground index missing. Try running the 'init' command to create it."
                raise FileNotFoundError(error_msg)
            raise IndexError(f'"{self.id_num}" is not a valid campground id.')

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
        if not width:
            width = len(self.name)
        width += 22

        if error:
            col_1 = f"<question>{self.name}</question>"
            col_2 = f"<error>{error}</>"
        else:
            try:
                num_available_sites = len(self.available)
            except AvailabilityNotFoundError:
                raise

            if 1 <= num_available_sites <= 12:
                sorted_sites = ", ".join(self.available)
                col_1 = f"<question>{self.name}</question>:"
                col_2 = f"<fg=yellow>{sorted_sites}</> available"

            elif num_available_sites > 12:
                col_1 = f"<question>{self.name}</question>:"
                col_2 = f"<fg=green>{num_sites_available}</> sites available"

            else:
                col_1 = f"<question>{self.name}</question>:"
                col_2 = f"<fg=red>full</>"

        self._cli_text = f"{col_1:{width}} {col_2}" 
        return self._cli_text 


