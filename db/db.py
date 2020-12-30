import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self, db_filename: str):
        try:
            self.conn = sqlite3.connect(db_filename)
        except Error as e:
            print(e)

    def execute_query_nr(self, unformatted_query: str, arguments: tuple):
        """ Does a query but doesn't return anything """
        cursor = self.conn.cursor()
        cursor.execute(unformatted_query, arguments)

    def execute_query(self, unformatted_query: str, arguments: tuple):
        """ Queries and returns the rows """
        cursor = self.conn.cursor()
        cursor.execute(unformatted_query, arguments)
        rows = cursor.fetchall()
        return rows

    def add_row(self, unformatted_query: str, arguments: tuple):
        """ Returns the row that was just added """
        cur = self.conn.cursor()
        cur.execute(unformatted_query, arguments)
        self.conn.commit()
        return cur.lastrowid
