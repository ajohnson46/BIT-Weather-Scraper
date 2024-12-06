from guizero import App, Text, PushButton
from db_operations import DBOperations
from scrape_weather import GCWeatherParser
from datetime import date, timedelta
from plot_operations import PlotOperations
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class WeatherProcessor():
    """Handles all user interactions and manages weather data processing."""

    def __init__(self):
        """Initialize the database connection."""
        self.db = DBOperations()
        self.app = App(title="Weather Data Processor", width=400, height=300)
        self.setup_menu()
        self.plot_canvas = None

    def setup_menu(self):
        """"""
        Text(self.app, text="Weather Data Processor", size=20, font="Helvetica", color="black")

        PushButton(self.app, text="Download Full Weather Data", command=self.download_full_data)
        PushButton(self.app, text="Update Weather Data", command=self.update_weather_data)
        PushButton(self.app, text="Generate Box Plot for Year Range", command=self.generate_box_plot)
        PushButton(self.app, text="Generate Line Plot for Specific Month", command=self.generate_line_plot)

    def clear_previous_plot(self):
        """Remove any existing plot canvas from the GUI."""
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().pack_forget()
            self.plot_canvas = None

    def download_full_data(self):
        """Download the full weather dataset by purging existing data and rescraping."""
        try:
            print("Starting the data download process...")
            # Purge the existing database
            #self.db.purge_data()

            #Use the GCWeatherParser to fetch and save data
            parser = GCWeatherParser()
            working_day = date.today()
            print(f"Starting with today's date: {working_day}")

            #weather_data = parser.fetch_weather_data(working_day)
            existing_data = self.db.fetch_data(year=working_day.year)
            print(f"Fetched existing data for year {working_day.year}: {len(existing_data)} records found")

            # Save the fetched data to the database
            for data in existing_data:
                print(f"Saving data: {data}")
                self.db.save_data(data)


            self.show_message("Download Complete", "Full weather data downloaded successfully.")

        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")

    def update_weather_data(self):
        try:
            #  Get the latest date in the database
            records = self.db.fetch_data()
            if not records:
                self.show_message("No Data Found", "No existing data found. Please download the full dataset first.")
                return

            # Calculate the date range to scrape
            latest_date_str = max(record[1] for record in records)
            latest_date = date.fromisoformat(latest_date_str)
            today = date.today()
            if latest_date >= today:
                self.show_message("Update Not Needed", "The database is already up-to-date.")
                return

            # Use GCWeatherParser to fetch and save missing data
            parser = GCWeatherParser()
            working_day = latest_date + timedelta(days=1)  # Start from the day after the latest date

            while working_day <= today:
                year = working_day.year
                month = working_day.month

                # Generate URL (moved to parser's responsibility if needed)
                url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year={year}&Month={month}#"

                parser.date = working_day
                parser.feed(url)  # Assuming parser already handles downloading and parsing

                # Save parsed data to the database
                for day, data in parser.weatherData.items():
                    db_data = {
                        "sample_date": day,
                        "location": "Winnipeg",
                        "min_temp": data["min"],
                        "max_temp": data["max"],
                        "avg_temp": data["mean"],
                    }
                    self.db.save_data(db_data)

                # Move to the next day
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

                self.clear_previous_plot()  # Clear any previous plot from the GUI
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

                self.clear_previous_plot()  # Clear any previous plot from the GUI
            except Exception as e:
                self.show_message("Error", f"An error occurred: {str(e)}")

    def get_user_input(self, prompt):
        #Helper function to get user input via dialog
        return self.app.question("Input Required", prompt)

    def show_message(self, title, message):
        #Helper function to display a message to the user
        self.app.info(title, message)

    def run(self):
        self.app.display()


if __name__ == "__main__":
    processor = WeatherProcessor()
    processor.run()

