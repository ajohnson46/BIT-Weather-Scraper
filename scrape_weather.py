from html.parser import HTMLParser
import urllib.request

class GCWeatherParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.weatherData = {}
        self.in_row = False
        self.in_th = False

    def handle_starttag(self, tag, attrs):
        # th[scope=row] has the day. After, the data will be weather info. Non-numeric can be ignored.
        if tag == "th" and ('scope','row') in attrs:
            # We know that a TH is starting.
            # I'll need to know that the tag is TH later...
            self.in_row = True
            self.in_th = True # Not just in TH, but specifically the ones we like

        # td, while in row, would be Max, then Min, then Mean, and then others. Need to count.

    def handle_endtag(self, tag):
        if tag == "tr":
            self.in_row = False
        if tag == "th":
            self.in_th = False

    def handle_data(self, data):
        data = data.strip()
        # When we see data, we need to know if we are in the TH...
        # "When we..." = We are here now, and can check what 'data' is or what our variables have
        # "...we need to know..." = There should be a variable that was set up previously
        # "...if we are in..." = There's a condition that is set up. We're looking for a boolean concept.
        if self.in_row:
            if self.in_th: # This is specifically the beginning of the row.
                # if it's not numeric, just return... (this is probably not the best way to do it)
                try:
                    data = int(data)
                except:
                    return
                self.weatherData[data] = []    
            else: # other parts of the row....
                # We need to knw if we're in a td? The first, second, or third tds?
                print("other data from row: "+data)

parser = GCWeatherParser()

url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year=2018&Month=5#"

with urllib.request.urlopen(url) as response:
    html = response.read().decode('utf-8')

parser.feed(html)

print (parser.weatherData)