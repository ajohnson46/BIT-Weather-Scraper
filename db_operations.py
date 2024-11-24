"""
Description: Demonstrates DB operations, creates, inserts, deletes, & fetches
Date: Nov.23/2024
"""
import sqlite3

class DBOperations:

    def __init__(self, db_name="weather.sqlite"):
        """Initialize the database connection."""
        self.db_name = db_name
        self.conn = None
        #should be called anytime program is ran
        self.initialize_db()
    
    def initialize_db(self):
        """Intializes DB and creates table """
        try:
            self.conn = sqlite3.connect(self.db_name)
            c = self.conn.cursor()
            #query to create table if it doesn't already exist
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

#wasn't in assignment requirements, added in just in case - from topic challenge on DBs
   # def insert(self, sample_data):
    #    """Insert the given data into the DB"""
     #   try:
      #      #query to insert data in weather tbl
      #      sql = """insert into weather (sample_date, location, min_temp, max_temp, avg_temp)
      #       values (?,?,?,?,?)"""
      #      c = self.conn.cursor()
       #     for date, data in sample_data.items():
       #         location = data.get('Location', 'Unknown')
        #        c.execute(sql, (date, location, data['Min'], data['Max'], data['Mean']))
        #    self.conn.commit()
        #    print("Data Inserted successfully.")
        #except Exception as e:
        #    print("Error inserting sample.", e)

    def fetch_data(self):
        """fetches the data currently in the DB
        returns a list of tuples containing the data """
        try:
            #query to fetch all the data in the weather tbl
            sql = "SELECT * FROM weather"
            c = self.conn.cursor()
            c.execute(sql)
            #put into a tuple that contains the data, this is what is returned
            results = c.fetchall()
            print("Data fetched successfully")
            return results
        except Exception as e:
            print("Error fetching data.", e)
            return []
        
    def save_data(self, data):
        """ saves new data to the DB only if it doesn't already exist
         if the record does exist, it will be updated """
        try:
            sql = """INSERT INTO weather (sample_date, location, min_temp, max_temp, avg_temp)
                 VALUES (?, ?, ?, ?, ?)
                 ON CONFLICT(sample_date, location) DO UPDATE SET
                 min_temp = excluded.min_temp,
                 max_temp = excluded.max_temp,
                 avg_temp = excluded.avg_temp"""
            c = self.conn.cursor()
            c.execute(sql, (data["sample_date"], data["location"], data["min_temp"], data["max_temp"], data["avg_temp"]))
            self.conn.commit()
            print("Data saved or updated successfully.")
        except Exception as e:
            print("Error saving/updating data.", e)


    def purge_data(self):
        """ purge all the data from the DB for when program fetches all new weather data 
        (doesn't delete the DB just the data) """
        try:
            #deletes all rows in the weather table, but not the actual DB
            sql = "DELETE FROM weather"
            c = self.conn.cursor()
            c.execute(sql)
            self.conn.commit()
            print("Data deleted successfully.")
        except Exception as e:
            print("Error purging data.", e)
    
    def close_connection(self):
        """Closes the DB connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    db_ops = DBOperations()
