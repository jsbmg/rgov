import datetime


class Dates:
    def __init__(self, arrival_date, length_of_stay):
        self._arrival_date = self.__validate_date(arrival_date)
        self.length_of_stay = self.__validate_length(length_of_stay)
        self._request_dates = None
        self._stay_dates = None

    def __validate_date(self, date):
        """Validates the given date and returns it as a datetime
        object."""
        try:
            dt = datetime.datetime.strptime(date, "%m-%d-%Y")
        except ValueError:
            raise ValueError(
                f'"{date}" is not a valid date of the form mm-dd-yyyy'
            )
        if datetime.datetime.today().date() > dt.date():
            raise ValueError(f'"{date}" is not a future date.')
        return dt

    def __validate_length(self, length):
        """Validates the given length of stay and returns it as an
        integer."""
        if length.isnumeric():
            return int(length)
        else:
            raise ValueError('"{length_input}" is not an integer.')

    @property
    def request_dates(self):
        if self._request_dates is not None:
            return self._request_dates
        else:
            dates = []
            arrive = self._arrival_date.replace(day=1)
            time_delta = datetime.timedelta(days=self.length_of_stay)
            depart = self._arrival_date + time_delta
            for month in range(arrive.month, (depart.month + 1)):
                date = arrive.replace(month=month)
                date = date.strftime("%Y-%m-%dT00:00:00.000Z")
                dates.append(date)
            self._request_dates = dates
            return self._request_dates

    @property
    def stay_dates(self):
        if self._stay_dates is not None:
            return self._stay_dates
        else:
            stay_dates = []
            stay_range = range(self.length_of_stay)
            for i in stay_range:
                date = self._arrival_date + datetime.timedelta(days=i)
                date = date.strftime("%Y-%m-%dT00:00:00Z")
                stay_dates.append(date)
            self._stay_dates = stay_dates
            return self._stay_dates
