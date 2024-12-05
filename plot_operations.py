from db_operations import DBOperations
import matplotlib.pyplot as plt
import numpy as np

class PlotOperations:
    def test (self):
        db = DBOperations()
        weather_data = db.fetch_data()
        spread = []
        center = []
        flier_high = []
        flier_low = []
        monthly_data = {}

        for data in weather_data:
            month = data[1][5:7]
            if month not in monthly_data.keys():
                # count of days. sum of avgs, max for the month, and the min for month, list of raw averages
                monthly_data[month] = [1,data[5],data[3],data[4],[]]
                continue
            monthly_data[month][0] += 1
            monthly_data[month][1] += data[5]
            if monthly_data[month][2] < data[3]:
                monthly_data[month][2] = data[3]
            if monthly_data[month][3] > data[4]:
                monthly_data[month][3] = data[4]
            monthly_data[month][4].append(data[5]) 

            print (data)
            print (data[1][5:7])

        # if not data???

        print (monthly_data)

        monthly_data = dict(sorted(monthly_data.items()))

        data = []

        # count of days. sum of avgs, max for the month, and the min for month
        for key,item in monthly_data.items():
            data.append(item[4])
            # spread.append(item[2])
            # spread.append(item[3])
            # center.append(item[1]/item[0])
            # flier_high.append(item[2])
            # flier_low.append(item[3])
        
        # plot_data = np.concatenate((spread, center, flier_high, flier_low), 0)
        plt.boxplot(data)
        plt.show()
        plt.plot(data[0])
        plt.show()

        # d = np.random.normal(5,10,15)
        # print(d)

if __name__ == '__main__':
    plotter = PlotOperations()
    plotter.test()