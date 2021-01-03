import sqlite3
from shutil import copy

DB_FILE_BASE = "db/"


class Database:
    def __init__(self, db_filename: str):
        def touch(path):  # Makes an empty file because connect requires the file to exist
            import os
            with open(path, 'a'):
                os.utime(path, None)
            return path

        try:
            self.conn = sqlite3.connect(db_filename)
        except sqlite3.OperationalError:  # If error happens due to filename not existing, make the file and try again
            self.conn = sqlite3.connect(touch(db_filename))
        self.filename = db_filename

    def execute_commit_query(self, unformatted_query: str, arguments: tuple):
        """ Does a query but doesn't return anything """
        if not isinstance(arguments, tuple):
            arguments = (arguments,)

        cursor = self.conn.cursor()
        cursor.execute(unformatted_query, arguments)
        self.conn.commit()

    def execute_query(self, unformatted_query: str, arguments: tuple):
        """ Queries and returns the rows """
        if not isinstance(arguments, tuple):
            arguments = (arguments,)

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
        if not isinstance(arguments, tuple):
            arguments = (arguments,)
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
