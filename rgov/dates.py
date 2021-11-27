import datetime

class Dates:

    def __init__(self, arrival_date, length_of_stay):
        self._arrival_date = self.__validate_arrival_date(arrival_date)
        self.length_of_stay = self.__validate_length_of_stay(length_of_stay) 
        self._request_dates = None
        self._stay_dates = None

    def __validate_arrival_date(self, date_input):
        try:
            arrival_date = datetime.datetime.strptime(date_input, "%m-%d-%Y")
        except ValueError:
            raise ValueError(f'"{date_input}" is not a valid date of the form mm-dd-yyyy')
        if datetime.datetime.now() > arrival_date:
            raise ValueError(f'"{date_input}" is not a future date.')
        return arrival_date

    def __validate_length_of_stay(self, length_input):
        if length_input.isnumeric():
            return int(length_input)
        else:
            raise ValueError('"{length_input}" is not an integer.')

    @property
    def request_dates(self):
        if not self._request_dates == None:
            return self._request_dates
        else:
            request_dates = []
            first_day = self._arrival_date.replace(day=1)
            last_day = self._arrival_date + datetime.timedelta(days=self.length_of_stay)
            for month in range(first_day.month, (last_day.month + 1)):
                request_date = first_day.replace(month=month)
                request_date = request_date.strftime("%Y-%m-%dT00:00:00.000Z")
                request_dates.append(request_date)
            self._request_dates = request_dates
            return self._request_dates
    
    @property
    def stay_dates(self):
        if not self._stay_dates == None:
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
