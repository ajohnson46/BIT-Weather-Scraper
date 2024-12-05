from db_operations import DBOperations
import matplotlib.pyplot as plt
import numpy as np

class PlotOperations:
    """Pulls data from the weather database and displays a box plot for all the data and a line plot for the month selected.
    """
    def __init__(self, year=None):
        # Handle what happens when you don't choose a year
        self.year = year

    def test (self):
        db = DBOperations()
        weather_data = db.fetch_data() # Need a way to fetch only a single year
        monthly_data = {}

        # For all data this year, split into months and store each set of monthly data 
        # WARNING: This needs the data to only be for one year.
        for data in weather_data:
            month = data[1][5:7]
            year = int(data[1][0:4])
            # If this is not for the chosen year, skip
            if self.year != year:
                continue
            # Set up array so we can append into it
            if month not in monthly_data.keys():
                monthly_data[month] = []
            monthly_data[month].append(data[5]) 

        # if not data???

        # Sort by month
        monthly_data = dict(sorted(monthly_data.items()))

        # Array of each month of data, for boxplot.
        # Can pull out one month for line chart.
        data = []
        for key,item in monthly_data.items():
            data.append(item)
        
        plt.boxplot(data)
        plt.show()
        plt.plot(data[0])
        plt.show()


# Just for testing.
if __name__ == '__main__':
    year = "2024"
    # can change it to int or can handle strings elsewhere...
    year = int(year)
    plotter = PlotOperations(year)
    
    plotter.test()