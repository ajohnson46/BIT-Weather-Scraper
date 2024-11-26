"""
Description: Context manager to manage DB connections
Date: Nov.24/2024
"""
import sqlite3

class DBCM:

    def __init__(self, db_name="weather.sqlite"):
        """Initialize the database connection."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """establish connection and return a cursor"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return self.cursor
        except sqlite3.Error as e:
            print("Error connecting to the database:", e)
            return None
        
    def __exit__(self,  exc_type, exc_value, traceback):
        """commit changes and closr the DB"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:  #no exception occurred
                self.conn.commit()
            else:  #exception occurred
                print("An error occurred, rolling back changes.")
                self.conn.rollback()
            self.conn.close()

