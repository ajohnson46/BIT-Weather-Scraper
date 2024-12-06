from db_operations import DBOperations
import matplotlib.pyplot as plt
import numpy as np

class PlotOperations:
    """Pulls data from the weather database and displays a box plot for all the data and a line plot for the month selected.
    """
    def __init__(self, db):
        # Handle what happens when you don't choose a year
        self.db = db

    def generate_box_plot(self, year_from, year_to, output_file=None):
        #db = DBOperations()
       # weather_data = db.fetch_data(year=self.year) 
       # monthly_data = {}

        # For all data this year, split into months and store each set of monthly data 
        # WARNING: This needs the data to only be for one year.
       # for data in weather_data:
        #    month = data[1][5:7]
            #year = int(data[1][0:4])
            # If this is not for the chosen year, skip
            #if self.year != year:
            #    continue
            # Set up array so we can append into it
          #  if month not in monthly_data:
           #     monthly_data[month] = []
          #  monthly_data[month].append(data[5]) 

        # if not data???

        # Sort by month
        #monthly_data = dict(sorted(monthly_data.items()))

        # Array of each month of data, for boxplot.
        # Can pull out one month for line chart.
        #data = []
       # for key,item in monthly_data.items():
        #    data.append(item)

        #data = [temps for temps in monthly_data.values()]
         #data = self.get_data_for_year_range(year_from, year_to)

        records = self.db.fetch_data()
        filtered_data = [
            record for record in records
            if year_from <= int(record[1].split("-")[0]) <= year_to
        ]

        if not filtered_data:
            raise ValueError("No data available for the specified year range.")

        # Extract temperatures
        temps = [record[4] for record in filtered_data if record[4] is not None]

        if not temps:
            raise ValueError("No temperature data available for the specified range.")
        # Generate and show the box plot
        plt.figure(figsize=(10, 6))
        #plt.boxplot(data)
        plt.boxplot(temps, vert=True, patch_artist=True)
        plt.title(f"Box Plot of Temperatures ({year_from} to {year_to})")
        #plt.xlabel("Years")
        plt.ylabel("Temperature (°C)")
        
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()

    def generate_line_plot(self, year, month, output_file=None):
        """Generate a line plot for a specific month in the specified year."""   
        #db = DBOperations()
        #weather_data = db.fetch_data(year=self.year)

        # Extract data for the specified month
        #daily_data = []
        #for data in weather_data:
        #    if data[1][5:7] == month:
          #      daily_data.append(data[5])  # Append avg_temp
        
        #if not daily_data:
        #    print(f"No data available for {self.year}-{month}.")
         #   return
        records = self.db.fetch_data()
        filtered_data = [
            record for record in records
            if int(record[1].split("-")[0]) == year and int(record[1].split("-")[1]) == month
        ]

        if not filtered_data:
            raise ValueError("No data available for the specified month and year.")

        # Extract dates and temperatures
        dates = [record[1] for record in filtered_data]
        temps = [record[4] for record in filtered_data if record[4] is not None]

        if not temps:
            raise ValueError("No temperature data available for the specified month.")

        # Generate and show the line plot
        plt.figure(figsize=(10, 6))
        #plt.plot(range(1, len(daily_data) + 1), daily_data, marker='o')
        plt.plot(dates, temps, marker="o", linestyle="-", color="b")
        plt.title(f"Line Plot of Temperatures ({year}-{month:02})")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()