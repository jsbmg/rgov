import csv
import datetime
import json

from urllib.request import Request, urlopen
from urllib.parse import urlencode

from fake_useragent import UserAgent

from rgov.utils import constants

BASE_URL = "https://www.recreation.gov/api/camps/availability/campground/"
BROWSER_BASE_URL = "https://www.recreation.gov/camping/campgrounds/"
REQUEST_TIME_FORMAT = "%Y-%m-%dT00:00:00.000Z"
RESPONE_TIME_FORMAT = "%Y-%m-%dT00:00:00Z"

def get_campground_name(campground_id):
    "Get a campground's name from it's numerical id."
    with open(constants.index_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if campground_id in row[0]:
                return row[1].title()
    return "title n/a"

def get_request_dates(arrival_date, length_of_stay):
    "Generate dates for the Recreation.gov api request."
    request_dates = []
    first_day = arrival_date.replace(day=1)
    last_day = arrival_date + datetime.timedelta(days=length_of_stay)
    for month in range(first_day.month, (last_day.month + 1)):
        rqst_date = first_day.replace(month=month)
        rqst_date_fmtd = rqst_date.strftime(constants.request_time_format)
        request_dates.append(rqst_date_fmtd)
    return request_dates

def get_stay_dates(arrival_date, length_of_stay):
    "Returns list of all dates of stay."
    stay_dates = []
    stay_range = range(length_of_stay)
    for i in stay_range:
        date = arrival_date + datetime.timedelta(days=i)
        date_formatted = date.strftime(constants.response_time_format)
        stay_dates.append(date_formatted)
    return stay_dates

def request(request_dates, campground_id):
    requests = []
    for date in request_dates:
        url = f"{constants.base_url}{campground_id}/month?"
        params = {"start_date": date}
        query_string = urlencode(params)
        url = url + query_string
        req = Request(url)
        req.add_header("User-Agent", UserAgent().random)
        data = urlopen(req)
        data = data.read()
        data_loaded = json.loads(data)
        try:
            campsite_data = data_loaded["campsites"]
        except KeyError as e:
            raise UnboundLocalError("Invalid ID")
        requests.append(campsite_data.values())
    return requests
    
def get_available_sites(requests, stay_dates):
    unavailable_sites = []
    last_day = stay_dates[-1]
    for request in requests:
        for site in request:
            for date in stay_dates:
                if date in site["availabilities"]:
                    if site["availabilities"][date] not in "Available":
                        break
                    else:
                        if date == last_day:
                            unavailable_sites.append(site["site"])
    return unavailable_sites
 
         
def parse_arrival_date(date_input):
    try:
        arrival_date = datetime.datetime.strptime(date_input, "%m-%d-%Y")
    except ValueError:
        date_error_line = (
            f'"{date_input}" is not a valid date in the form mm-dd-yyyy'
        )
        raise ValueError(date_error_line)
    return arrival_date

def parse_length_of_stay(length_input):
    try:
        length_of_stay = int(length_input)
    except ValueError:
        length_error_line = f'"{length_input}" is not an integer'
        raise ValueError(length_error_line)
    return length_of_stay

def generate_campground_url(campground_id):
    return constants.browser_base_url + campground_id + "/availability"
    
