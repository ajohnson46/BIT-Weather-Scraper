from db_operations import DBOperations

class PlotOperations:
    def test (self):
        db = DBOperations()
        weather_data = db.fetch_data()

        for data in weather_data:

            print (data)

if __name__ == '__main__':
    plotter = PlotOperations()
    plotter.test()