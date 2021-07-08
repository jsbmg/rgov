import csv
import datetime
import json
import requests

from cleo import Command
from fake_useragent import UserAgent

from rgov.commands import paths


class CheckCommand(Command):
    base_url = "https://www.recreation.gov/api/camps/availability/campground/"
    headers = {"User-Agent": UserAgent().random}
    human_time_format = "%m/%d/%y"
    request_time_format = "%Y-%m-%dT00:00:00.000Z"
    response_time_format = "%Y-%m-%dT00:00:00Z"

    def main(self, campground_id):
        """Requests campground data and returns the name and a list of
        available sites for the given dates.

        Raises:
            UnboundLocalError: When the campground id is not recognized
        """
        # Get the name of the campground from the id. Iterates through the csv
        # until the id matches and assign the campground_name variable to the
        # corresponding name
        with open(paths.index_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if campground_id in row[0]:
                    campground_name = row[1].title()

        # Gather date and length of stay input, otherwise use the default
        # values
        if self.option("date"):
            date_input = self.option("date")
            try:
                arrival_date = datetime.datetime.strptime(date_input, "%m-%d-%Y")
            except ValueError:
                date_error_line = (f'"{date_input}" is not a valid date'
                              ' in the form mm-dd-yyyy')
                raise ValueError(date_error_line)
        else:
            arrival_date = datetime.date.today()
        if self.option("length"):
            length_input = self.option("length")
            try:
                length_of_stay = int(length_input)
            except ValueError:
                length_error_line = (f'"{length_input}" is not an integer')
                raise ValueError(length_error_line)
        else:
            length_of_stay = 3

        # Creates a list of request dates stored in the variable
        # "request_dates". The site requires that request dates be on the first
        # of the month, and in the format specified in the variable
        # request_time_format, so if the dates span into a new calendar month,
        # we need to generate more requests with the proper dates.
        request_dates = []
        first_day = arrival_date.replace(day=1)
        last_day = arrival_date + datetime.timedelta(days=length_of_stay)
        for month in range(first_day.month, (last_day.month + 1)):
            rqst_date = first_day.replace(month=month)
            rqst_date_fmtd = rqst_date.strftime(self.request_time_format)
            request_dates.append(rqst_date_fmtd)

        # Generate a list of the days thay we intend to camp on. This starts on
        # the arrival_date and spans the number of days in length_of_stay. This
        # is formatted how the response dates are formatted, so that we can
        # select values from the responses data using this list.
        stay_dates = []
        stay_range = range(length_of_stay)
        for i in stay_range:
            date = arrival_date + datetime.timedelta(days=i)
            date_formatted = date.strftime(self.response_time_format)
            stay_dates.append(date_formatted)

        # Requests campground availability date for the request dates created
        # above, and stores each response in a list. If the response is empty
        # it may be an invalid id, so the function will return with
        # "INVALID_ID".
        url = f"{self.base_url}{campground_id}/month?"
        responses = []
        for date in request_dates:
            data = requests.get(url, {"start_date": date}, headers=self.headers)
            data_loaded = json.loads(data.text)
            try:
                campsite_data = data_loaded["campsites"]
            except KeyError as e:
                raise UnboundLocalError("Invalid ID")
            campsite_values = campsite_data.values()
            responses.append(campsite_values)

        # Create a list of all sites for the campground. Iterate through the
        # responses, appending sites to the unavailable_sites list if they are
        # unavailable on any of the stay dates. Create a list of all sites that
        # aren't unavailable, and return that.
        all_sites = [site["site"] for site in responses[0]]
        unavailable_sites = []
        for response in responses:
            for site in response:
                for date in stay_dates:
                    if date in site["availabilities"]:
                        if site["availabilities"][date] not in "Available":
                            unavailable_sites.append(site["site"])
                            break
        available_sites = [site for site in all_sites if site not in unavailable_sites]

        # raise ValueError if campground_name is empty
        try:
            return campground_name, available_sites
        except UnboundLocalError as e:
           raise UnboundLocalError('Invalid campground ID')
