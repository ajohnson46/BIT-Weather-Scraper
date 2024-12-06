"""
Description: Demonstrates DB operations, creates, inserts, deletes, & fetches
Date: Nov.23/2024
"""
from dbcm import DBCM

class DBOperations:

    def __init__(self, db_name="weather.sqlite"):
        """Initialize the database connection."""
        self.db_name = db_name
        #should be called anytime program is ran
        self.initialize_db()
    
    def initialize_db(self):
        """Intializes DB and creates table """
        try:
            with DBCM(self.db_name) as c:
                #query to create table if it doesn't already exist
                c.execute("""CREATE TABLE IF NOT EXISTS weather
                            (id integer primary key autoincrement not null,
                            sample_date text not null,
                            location text not null,
                            min_temp real,
                            max_temp real,
                            avg_temp real,
                            UNIQUE(sample_date, location)
                      );""")
            print("DB initialized and table created")
        except Exception as e:
            print("Error creating table:", e)

    def fetch_data(self, year=None):
        """Fetches data from the DB, optionally filtered by year."""
        try:
            with DBCM(self.db_name) as c:
                if year:
                   sql = "SELECT * FROM weather WHERE sample_date LIKE ?"
                   c.execute(sql, (f"{year}%",))
                else:
                    sql = "SELECT * FROM weather"
                    c.execute(sql)
                results = c.fetchall()
                print("Fetched data:", results)  # Debug output
                return results
        except Exception as e:
             print("Error fetching data:", e)
             return []
        
    def save_data(self, data):
        """ saves new data to the DB only if it doesn't already exist
         if the record does exist, it will be updated """
        try:
            with DBCM(self.db_name) as c:
                print(f"Saving data: {data}")  # Debug output
                sql = """INSERT INTO weather (sample_date, location, min_temp, max_temp, avg_temp)
                 VALUES (?, ?, ?, ?, ?)
                 ON CONFLICT(sample_date, location) DO UPDATE SET
                 min_temp = excluded.min_temp,
                 max_temp = excluded.max_temp,
                 avg_temp = excluded.avg_temp"""
                c.execute(sql, (data["sample_date"], data["location"], data["min_temp"], data["max_temp"], data["avg_temp"]))
                
        except Exception as e:
            print(f"When saving {data['sample_date']}: {e}")

    def purge_data(self):
        """ purge all the data from the DB for when program fetches all new weather data 
        (doesn't delete the DB just the data) """
        try:
            #deletes all rows in the weather table, but not the actual DB
            with DBCM(self.db_name) as c:
                sql = "DELETE FROM weather"
                c.execute(sql)
                print("Data deleted successfully.")
        except Exception as e:
            print("Error purging data.", e)


if __name__ == "__main__":
    db_ops = DBOperations()
