from datetime import date, timedelta
from guizero import App, Text, PushButton, Box
from db_operations import DBOperations
from scrape_weather import GCWeatherParser
from plot_operations import PlotOperations
class WeatherProcessor():
    """Handles all user interactions and manages weather data processing."""
    def __init__(self):
        """Initialize the database connection."""
        self.db = DBOperations()
        self.app = App(title="Weather Data Processor", width=500, height=400)
        self.setup_menu()
        self.plot_canvas = None

    def setup_menu(self):
        """Sets up all components of the GUI menu"""
        #header set up
        header_box = Box(self.app, align="top")
        Text(header_box, text="Weather Data Processor", size=20, font="Helvetica", 
             color="black", align="top")
        Text(header_box, text="Manage and visualize weather data", size=10, font="Helvetica",
              color="black")
        Text(self.app, text="") #spacer
        #button container set up
        button_box = Box(self.app, align="top", border=True) 
        button_padding = {"width": 25, "height": 2}
        button_box.bg = "black" #outline colour
        #action buttons
        PushButton(button_box, text="Download Full Weather Data", 
                   command=self.download_full_data, **button_padding)
        PushButton(button_box, text="Update Weather Data", 
                   command=self.update_weather_data, **button_padding)
        PushButton(button_box, text="Generate Box Plot for Year Range", 
                   command=self.generate_box_plot, **button_padding)
        PushButton(button_box, text="Generate Line Plot for Specific Month", 
                   command=self.generate_line_plot, **button_padding)
        Text(self.app, text="") #spacer
        #footer set up
        footer_box = Box(self.app, align="bottom") 
        Text(footer_box, text="Developed by Abigail Ferreira & Alyssa Johnson", 
             size=8, font="Helvetica", color="gray")
        #container colours
        self.app.bg = "lightgray"
        button_box.bg = "lightblue"

    def clear_previous_plot(self):
        """Remove any existing plot canvas from the GUI."""
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().pack_forget()
            self.plot_canvas = None

    def download_full_data(self):
        """Download the full weather dataset by rescraping 
        (using WeatherParser) and displaying success to user."""
        try:
            print("Starting the data download process...")
            working_day = date.today()
            print(f"Starting with today's date: {working_day}")
            existing_data = self.db.fetch_data(year=working_day.year)
            print(f"Fetched existing data for year {working_day.year}: {len(existing_data)} records found")

            #Save the fetched data to the database
            for data in existing_data:
                print(f"Saving data: {data}")
                print(f"Processing data tuple: {data}")
                #parsed to a tuple as save_data needs to accept this and not a dict.
                db_data = {
                    "id": data[0],
                    "sample_date": data[1],
                    "location": data[2],
                    "min_temp": data[3],
                    "max_temp": data[4],
                    "avg_temp": data[5],
                }
                self.db.save_data(db_data)

            self.show_message("Download Complete", "Full weather data downloaded successfully.")

        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")

    def update_weather_data(self):
        """Update the full weather data set by fetching 
        data records and saving/updating any records"""
        try:
            print("Starting weather data update process...")
            records = self.db.fetch_data()
            if not records:
                self.show_message("No Data Found", 
                                  "No existing data found. Please download the full dataset first.")
                return
            
            #validate and find the latest valid date
            latest_date_str = None
            for record in records:
                try:
                    #attempt to parse the date field
                    date_candidate = record[1]
                    print(f"Checking date: {date_candidate}")
                    _ = date.fromisoformat(date_candidate)  #validates the format
                    latest_date_str = date_candidate if not latest_date_str else max(latest_date_str, date_candidate)
                except ValueError as e:
                    print(f"Invalid date format in record: {record} - {e}")
            
            #calculate the date range to scrape
            latest_date_str = max(record[1] for record in records)
            print(f"Latest date in database: {latest_date_str}")

            if not latest_date_str:
                print("No valid dates found in the database.")
                self.show_message("Error", "No valid dates found in the database.")
                return

            print(f"Latest valid date in database: {latest_date_str}")
            latest_date = date.fromisoformat(latest_date_str)

            today = date.today()
            if latest_date >= today:
                self.show_message("Update Not Needed", "The database is already up-to-date.")
                return
            #use GCWeatherParser to fetch and save missing data
            parser = GCWeatherParser()
            working_day = latest_date + timedelta(days=1)  

            while working_day <= today:
                year = working_day.year
                month = working_day.month

                #generate URL 
                url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year={year}&Month={month}#"

                parser.date = working_day
                parser.feed(url)  #parser already handles downloading and parsing

                #save parsed data to the database
                for day, data in parser.weatherData.items():
                    db_data = {
                        "sample_date": day,
                        "location": "Winnipeg",
                        "min_temp": data["min"],
                        "max_temp": data["max"],
                        "avg_temp": data["mean"],
                    }
                    self.db.save_data(db_data)

                #move to the next day
                working_day += timedelta(days=1)
            self.show_message("Update Complete", "Weather data updated successfully.")
        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")

    def generate_box_plot(self):
        """Generate box plot for a user-specified year range."""
        year_from = self.get_user_input("Enter the starting year:")
        year_to = self.get_user_input("Enter the ending year:")

        if year_from and year_to:
            try:
                plotter = PlotOperations(self.db)
                plotter.generate_box_plot(int(year_from), int(year_to))
                self.clear_previous_plot()  #clear any previous plot from the GUI
            except Exception as e:
                self.show_message("Error", f"An error occurred: {str(e)}")

    def generate_line_plot(self):
        """Generate line plot for a specific month and year."""
        year = self.get_user_input("Enter the year:")
        month = self.get_user_input("Enter the month (1-12):")

        if year and month:
            try:
                plotter = PlotOperations(self.db)
                plotter.generate_line_plot(int(year), int(month))
                self.clear_previous_plot()  #clear any previous plot from the GUI
            except Exception as e:
                self.show_message("Error", f"An error occurred: {str(e)}")

    def get_user_input(self, prompt):
        """Gets user input via dialog prompt"""
        return self.app.question("Input Required", prompt)

    def show_message(self, title, message):
        """Displays messages to user (error messages for ex.)"""
        self.app.info(title, message)

    def run(self):
        """Runs the application & displays GUI"""
        self.app.display()


if __name__ == "__main__":
    processor = WeatherProcessor()
    processor.run()

