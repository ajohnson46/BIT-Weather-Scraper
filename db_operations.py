"""
Description: Demonstrates DB operations, creates, inserts, & fetches
Author: Abigail Ferreira
Date: Oct.13/2024
"""
import sqlite3

class DBOperations:

    def __init__(self, db_name="weather.sqlite"):
        """Initialize the database connection."""
        self.db_name = db_name
        self.conn = None
    
    def initialize_db(self):
        """Intializes DB and creates table """
        try:
            self.conn = sqlite3.connect(self.db_name)
            c = self.conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS weather
                            (id integer primary key autoincrement not null,
                            sample_date text not null,
                            location text not null,
                            min_temp real not null,
                            max_temp real not null,
                            avg_temp real not null,
                            UNIQUE(sample_date, location)
                      );""")
            self.conn.commit()
            print("DB initialized and table created")
        except Exception as e:
            print("Error creating table:", e)

    def insert(self, sample_data):
        """Insert the given data into the DB"""
        try:
            sql = """insert into weather (sample_date, location, min_temp, max_temp, avg_temp)
             values (?,?,?,?,?)"""
            c = self.conn.cursor()
            for date, data in sample_data.items():
                location = data.get('Location', 'Unknown')
                c.execute(sql, (date, location, data['Min'], data['Max'], data['Mean']))
            self.conn.commit()
            print("Data Inserted successfully.")
        except Exception as e:
            print("Error inserting sample.", e)

    def fetch_data(self):
        """fetches the data currently in the DB
        returns a list of tuples containing the data """
        try:
            sql = """SELECT sample_date, location, min_temp, max_temp, avg_temp FROM weather"""

            c = self.conn.cursor()
            c.execute(sql)
            results = c.fetchall()
            return results
        except Exception as e:
            print("Error fetching data.", e)
            return []
        
    def save_data(self):
        """ saves new data to the DB only if it doesn't already exist """


    def purge_data(self):
        """ purge all the data from the DB for when program fetches all new weather data 
        (doesn't delete the DB just the data) """
    

    def close_connection(self):
        """Closes the DB connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    db_ops = DBOperations()
