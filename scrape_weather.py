from html.parser import HTMLParser
import urllib.request
from datetime import date, timedelta
from db_operations import DBOperations

class GCWeatherParser(HTMLParser):
    """Stuff

    """
    def __init__(self):
        """Info about how it's made
        """
        super().__init__()
        self.weatherData = {}
        """A dictionary of dictionaries. Date ->  Min:int, Max:int, Mean:int """
        self.date = date.today() # Could be passed in somehow, like when parsing.
        self.finished = False
        """ """

        # Could be private:
        self.in_row = False
        self.in_th = False
        self.column_counter = 0

    def handle_starttag(self, tag, attrs):
        # th[scope=row] has the day. After, the data will be weather info. Non-numeric can be ignored.
        if tag == "th" and ('scope','row') in attrs:
            # We know that a TH is starting.
            # I'll need to know that the tag is TH later...
            self.in_row = True
            self.in_th = True # Not just in TH, but specifically the ones we like
            self.column_counter = 0

        # td, while in row, would be Max, then Min, then Mean, and then others. Need to count.
        if tag == "td":
            self.column_counter += 1 

    def handle_endtag(self, tag):
        if tag == "tr":
            self.in_row = False
        if tag == "th":
            self.in_th = False

    def handle_data(self, data):
        data = data.strip()
         # if it's not numeric, just return... (this is probably not the best way to do it)
        try:
            data = float(data)
        except:
            if data and self.in_th:
                self.in_row = False # If row does not start with a number, this is not a row of data
            return
        # When we see data, we need to know if we are in the TH...
        # "When we..." = We are here now, and can check what 'data' is or what our variables have
        # "...we need to know..." = There should be a variable that was set up previously
        # "...if we are in..." = There's a condition that is set up. We're looking for a boolean concept.
        if self.in_row:
            daystring = self.date.isoformat()
            if self.in_th: # This is specifically the beginning of the row.
                self.date=self.date.replace(day = int(data))
                daystring = self.date.isoformat()
                # Creating the dictionary keys
                self.weatherData[daystring] = {"max": None, "min": None, "mean": None} 
            elif self.column_counter == 1:
                self.weatherData[daystring]["max"] = data
            elif self.column_counter == 2:
                self.weatherData[daystring]["min"] = data
            elif self.column_counter == 3:
                self.weatherData[daystring]["mean"] = data
            else: # other parts of the row....
                # We need to knw if we're in a td? The first, second, or third tds?
                # print(f"other data from row: {data}")
                pass

if __name__ == '__main__':
    parser = GCWeatherParser()
    workingDay = date.today()
    # workingDay = date.fromisoformat('1997-03-01') # TESTING VALUE, scrapes only two months.

    while parser.finished == False:
        year = workingDay.year
        month = workingDay.month

        #URL where month and year roll back as the loop continues
        url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year={year}&Month={month}#"

        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            # Prints a line of stars as it scrapes, to show progress
            print("*", end=" ")

        parser.date = workingDay
        parser.feed(html)
        daystring = parser.date.isoformat()


        #Print weather data for the month if available
        try:
            parser.weatherData[daystring]
            # Just for debugging. It'll print compoundingly more data, but it's hard to get just the keys for the month.
            # for day, data in parser.weatherData.items():
                # print(f"{day}: {data}")

        except KeyError:
            #Break the loop if there is no data found for the month
            print(f"No data available for {workingDay.strftime('%B %Y')}. Ending loop.")
            break

        #move to the previous month
        workingDay = workingDay.replace(day=1) - timedelta(days=1)

    # Saving the data
    db = DBOperations()
    #(data["sample_date"], data["location"], data["min_temp"], data["max_temp"], data["avg_temp"])
    for day, data in parser.weatherData.items():
        # Data = {min, max, mean}
        db_data = {}
        db_data ["sample_date"] = day
        db_data ["location"] = "Winnipeg"
        db_data ["min_temp"] = data ["min"]
        db_data ["max_temp"] = data ["max"]
        db_data ["avg_temp"] = data ["mean"]

        db.save_data(db_data)   
        