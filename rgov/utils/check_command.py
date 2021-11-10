import csv
import datetime
import json

from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from fake_useragent import UserAgent

from rgov.utils.constants import Paths, Time, Urls


def get_campground_name(campground_id: str) -> str:
    "Get a campground's name from it's numerical id."
    with open(Paths.index_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if campground_id in row[0]:
                return row[1].title()
            
    raise IndexError(f'"{campground_id}" is not a valid id.')

def get_request_dates(arrival_date: datetime.datetime, length_of_stay: int) -> list:
    "Generate dates for the Recreation.gov api request."
    request_dates = []
    first_day = arrival_date.replace(day=1)
    last_day = arrival_date + datetime.timedelta(days=length_of_stay)
    for month in range(first_day.month, (last_day.month + 1)):
        rqst_date = first_day.replace(month=month)
        rqst_date_fmtd = rqst_date.strftime(Time.request_time_format)
        request_dates.append(rqst_date_fmtd)
    return request_dates

def get_stay_dates(arrival_date: str, length_of_stay: int) -> list:
    "Get a list of all the dates that comprise the stay."
    stay_dates = []
    stay_range = range(length_of_stay)
    for i in stay_range:
        date = arrival_date + datetime.timedelta(days=i)
        date_formatted = date.strftime(Time.response_time_format)
        stay_dates.append(date_formatted)
    return stay_dates

def request(request_dates: list, campground_id: str) -> list:
    """Request availability data for month(s). Each request date must be the
first of the month, in the format defined in
rgov.utils.constants.Paths.request_time_format

    """
    # raise HTTPError('http://example.com', 500, 'Internal Error', {}, None)
    requests = []
    for date in request_dates:
        url = f"{Urls.base_url}{campground_id}/month?"
        params = {"start_date": date}
        query_string = urlencode(params)
        url = url + query_string
        req = Request(url)
        req.add_header("User-Agent", UserAgent().random)
        try:
            data = urlopen(req)
        except HTTPError:
            raise
        data = data.read()
        data_loaded = json.loads(data)
        try:
            campsite_data = data_loaded["campsites"]
        except KeyError:
            raise
        requests.append(campsite_data.values())
    return requests
    
def get_available_sites(requests: list[dict], stay_dates: list) -> list:
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
    return sorted(available_sites)
         
def parse_arrival_date(date_input: str) -> datetime:
    try:
        arrival_date = datetime.datetime.strptime(date_input, "%m-%d-%Y")
    except ValueError:
        date_error_line = (
            f'"{date_input}" is not a valid date in the form mm-dd-yyyy'
        )
        raise ValueError(date_error_line)
    return arrival_date

def parse_length_of_stay(length_input: str) -> int:
    try:
        length_of_stay = int(length_input)
    except ValueError:
        length_error_line = f'"{length_input}" is not an integer'
        raise ValueError(length_error_line)
    return length_of_stay

def generate_campground_url(campground_id: str) -> str:
    return Urls.browser_base_url + campground_id + "/availability"

def check(campground_id, request_dates, stay_dates):
    campground_name = get_campground_name(campground_id)
    try:
        data = request(request_dates, campground_id)
    except HTTPError:
        raise
    
    available_sites = get_available_sites(data, stay_dates)
    return campground_name, available_sites

def generate_cli_output(campground_name: str, available_sites: list) -> str:
    num_sites_available = len(available_sites)
    if 1 <= num_sites_available <= 12:
        sorted_sites = ", ".join(sorted(available_sites))
        text_output = (f"<question>{campground_name}</question> - "
        f"<info>site(s) {sorted_sites} available</info>.")
    elif num_sites_available > 12:
        text_output = (f"<question>{campground_name}</question> - "
        f"<info>{num_sites_available} sites available</info>.")
    else:
        text_output = (f"<question>{campground_name}</question> - "
        f"<fg=yellow>No sites available</fg=yellow>.")
    return text_output
    

