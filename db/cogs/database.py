import sqlite3
from sqlite3 import Error
from shutil import copy

DB_FILE_BASE = "/db/"


class Database:
    def __init__(self, db_filename: str):
        try:
            self.conn = sqlite3.connect(db_filename)
            self.filename = DB_FILE_BASE + db_filename
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

    def execute_query_no_arg(self, query: str):
        """ Does a query with no arguments """
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def add_row(self, unformatted_query: str, arguments: tuple):
        """ Returns the row id that was just added """
        cur = self.conn.cursor()
        cur.execute(unformatted_query, arguments)
        self.conn.commit()
        return cur.lastrowid

    def start_new_season(self, season_num: int):
        """ Helper method that makes a new db by coping the current one """
        new_filename = self.filename[:7] + str(season_num) + self.filename[-3:]  # follows format of `season-[num].db`
        copy(self.filename, new_filename)
        self.conn = sqlite3.connect(new_filename)
        self.filename = new_filename
