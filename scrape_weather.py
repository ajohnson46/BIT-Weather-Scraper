from html.parser import HTMLParser
import urllib.request
from datetime import date, timedelta
from db_operations import DBOperations

class GCWeatherParser(HTMLParser):
    """
    Parses HTML weather data from Environment Canada's website, extracting daily 
    weather statistics (max, min, and mean temperatures) for a given month.
    """
    def __init__(self):
        """
        Initializes the parser with attributes to track state and store weather data.
        """
        super().__init__()
        self.weatherData = {}
        """A dictionary of dictionaries storing weather data.
        Keys: ISO-formatted date strings.
        Values: Dictionaries with keys 'max', 'min', and 'mean' for temperature data.
        """
        self.date = date.today() # Could be passed in somehow, like when parsing.
        """Current date being processed. Can be updated dynamically."""
        self.finished = False
        """Flag to indicate when parsing is complete."""

        # Could be private:
        self.in_row = False
        """Tracks if the parser is inside a valid data row."""
        self.in_th = False
        """Tracks if the parser is inside a <th> element with row scope."""
        self.column_counter = 0
        """Tracks the column number for parsing specific temperature data."""

    def handle_starttag(self, tag, attrs):
        """
        Handles start tags in the HTML. Identifies <th> and <td> elements relevant to weather data.

        Args:
            tag (str): The name of the tag.
            attrs (list of tuples): Attributes of the tag.
        """
        # th[scope=row] has the day. After, the data will be weather info. Non-numeric can be ignored.
        if tag == "th" and ('scope','row') in attrs:
            # We know that a TH is starting.
            # I'll need to know that the tag is TH later...
            self.in_row = True
            self.in_th = True # Not just in TH, but specifically the ones we like
            self.column_counter = 0

        # td, while in row, would be Max, then Min, then Mean, and then others. Need to count.
        if tag == "td" and self.in_row:
            self.column_counter += 1

    def handle_endtag(self, tag):
        """
        Handles end tags in the HTML, resetting state variables for rows and headers.

        Args:
            tag (str): The name of the tag.
        """
        if tag == "tr":
            self.in_row = False
        if tag == "th":
            self.in_th = False

    def handle_data(self, data):
        """
        Processes the text content within tags, extracting relevant weather data.

        Args:
            data (str): The text content inside an HTML element.
        """
        data = data.strip()
         # if it's not numeric, just return... (this is probably not the best way to do it)
        try:
            data = float(data)
        except ValueError:
            if data and self.in_th:
                self.in_row = False # If row does not start with a number, this is not a row of data
            return
        # When we see data, we need to know if we are in the TH...
        # "When we..." = We are here now, and can check what 'data' is or what our variables have
        # "...we need to know..." = There should be a variable that was set up previously
        # "...if we are in..." = There's a condition that is set up. We're looking for a boolean concept.
        if self.in_row:
            daystring = self.date.isoformat()
            print(f"Handling data: {data}, Current Date: {self.date}, Column: {self.column_counter}")
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
    """
    Main script to scrape weather data, parse it, and save it to a database.
    """
    parser = GCWeatherParser()
    workingDay = date.today()
    # workingDay = date.fromisoformat('1997-03-01') # TESTING VALUE, scrapes only two months.

    while parser.finished == False:
        year = workingDay.year
        month = workingDay.month

        #URL where month and year roll back as the loop continues
        url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year={year}&Month={month}#"

        # Scrape the page
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
            print(f"Scraping URL: {url}")
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            break

        parser.date = workingDay
        parser.feed(html)
        daystring = parser.date.isoformat()


        #Print weather data for the month if available
        try:
            if daystring in parser.weatherData:
                print(f"Data for {workingDay.strftime('%B %Y')}: {parser.weatherData[daystring]}")
            else:
                print(f"No data available for {workingDay.strftime('%B %Y')}. Ending loop.")
                break
        except KeyError:
            print(f"No data found for {workingDay.strftime('%B %Y')}")
            break

        #move to the previous month
        workingDay = workingDay.replace(day=1) - timedelta(days=1)

    # Saving the data
    db = DBOperations()
    #(data["sample_date"], data["location"], data["min_temp"], data["max_temp"], data["avg_temp"])
    if parser.weatherData:
                    #print("Fetched data:", parser.weatherData)
        for day, data in parser.weatherData.items():
            if "min" in data and "max" in data and "mean" in data:
                print(f"Saving data: {data}")
                db_data = {
                    "sample_date": day,
                    "location": "Winnipeg",
                    "min_temp": data["min"],
                    "max_temp": data["max"],
                    "avg_temp": data["mean"],
                }
                db.save_data(db_data)
            else:
                print(f"Missing data for {day}, not saving.")
        