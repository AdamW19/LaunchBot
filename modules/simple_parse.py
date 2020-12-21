"""
This file provides a simple parser that is used in the interpretation of date strings. in the date subtractor.
"""
from datetime import datetime


def parse_raw_date_string(date_string: str):
    """
    Uses strptime to turn a string into a datetime and determines if there are no hours or minutes in the date string
    based on a trailing whitespace.
    :param date_string: The string containing the date to parse.
    :return: A tuple consisting of a datetime that was parsed from date_string and a boolean indicating if the date
             string contained hours or minutes based on trailing whitespace.
    """
    hours_and_minutes = True
    if date_string[len(date_string) - 1] == " ":
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d ")
        hours_and_minutes = False
    else:
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")

    return parsed_date, hours_and_minutes