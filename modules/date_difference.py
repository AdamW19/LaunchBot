"""
This file provides functionality for subtracting two dates from each other.
"""
from datetime import datetime
from dateutil.tz import tz

from modules import simple_parse
import calendar


class DateDifference:
    """
    Class that can store the difference between two dates, provides some overloaded functionality, and provides some
    static methods to subtract datetimes and formatted date strings.
    """

    def __init__(self, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0,
                 hours_and_minutes: bool = True):
        """
        Constructor for a DateDifference.
        :param years: The years field.
        :param months: The months field.
        :param days: The days field.
        :param hours: The hours field.
        :param minutes: The minutes field.
        :param hours_and_minutes: Whether to display hours and minutes when getting a string representation.
        """
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.hours_and_minutes = hours_and_minutes

    def __str__(self):
        """
        Generate a string representation of this DateDifference.
        :return: A string representation of this DateDifference.
        """
        year_string = ""
        if self.years == 1:
            year_string = "1 year"
        elif self.years != 0:
            year_string = str(self.years) + " years"

        month_string = ""
        if self.months == 1:
            month_string = ", 1 month"
        elif self.months != 0:
            month_string = ", " + str(self.months) + " months"

        day_string = ""
        if self.days == 1:
            day_string = ", 1 day"
        elif self.days != 0:
            day_string = ", " + str(self.days) + " days"

        hour_string = ""
        if self.hours == 1 and self.hours_and_minutes:
            hour_string = ", 1 hour"
        elif self.hours != 0 and self.hours_and_minutes:
            hour_string = ", " + str(self.hours) + " hours"

        minute_string = ""
        if self.minutes == 1 and self.hours_and_minutes:
            minute_string = ", 1 minute"
        elif self.minutes != 0 and self.hours_and_minutes:
            minute_string = ", " + str(self.minutes) + " minutes"

        output_string = year_string + month_string + day_string + hour_string + minute_string
        if len(output_string) > 0:
            if output_string[0] == ',':
                output_string = output_string[2:]
        else:
            output_string = "0 minutes"

        last_comma_index = -1
        num_commas = 0
        for i in range(0, len(output_string) - 1):
            if output_string[i] == ',':
                last_comma_index = i
                num_commas += 1
        if last_comma_index != -1 and num_commas > 1:
            output_string = output_string[:last_comma_index + 1] + " and" + output_string[last_comma_index + 1:]
        elif last_comma_index != -1 and num_commas == 1:
            output_string = output_string[:last_comma_index] + " and" + output_string[last_comma_index + 1:]

        return output_string

    def __le__(self, other):
        """
        Overloaded <= operator, compares every value.
        :param other: The other DateDifference being compared to.
        :return: Whether each value in this DateDifference is <= each value in other.
        """
        return (self.years <= other.years and
                self.months <= other.months and
                self.days <= other.days and
                self.hours <= other.hours and
                self.minutes <= other.minutes)

    @staticmethod
    def subtract_datetimes(date_1: datetime, date_2: datetime):
        """
        Figure out the difference of date_1 - date_2, accounting for various nuances that go into subtracting dates and
        times. Will subtract every field except seconds and microseconds.

        :param date_1: A datetime that will be on the left side of the subtraction.
        :param date_2: A datetime that will be on the right side of the subtraction.
        :return: A DateDifference holding the difference between the two dates.
        """
        if date_1.tzinfo is not None:
            date_1 = date_1.astimezone(tz.tzutc())

            if date_2.tzinfo is not None:
                date_2 = date_2.astimezone(tz.tzutc())
            else:
                raise AttributeError("date_1 has timezone information, but date_2 does not. "
                                     "date_1 and date_2 must either both have timezone information, or neither of them "
                                     " must have timezone information.")
        elif date_2.tzinfo is not None:
            raise AttributeError("date_2 has timezone information, but date_1 does not. "
                                 "date_1 and date_2 must either both have timezone information, or neither of them "
                                 " must have timezone information.")

        if date_1 >= date_2:
            bigger = date_1
            smaller = date_2
            return_as_negatives = False
        else:
            bigger = date_2
            smaller = date_1
            return_as_negatives = True

        year_difference = 0
        if bigger.year > smaller.year and (bigger.month > smaller.month or (
                bigger.month == smaller.month and bigger.day > smaller.day) or (
                    bigger.month == smaller.month and bigger.day == smaller.day and bigger.hour > smaller.hour) or (
                        bigger.month == smaller.month and bigger.day == smaller.day and bigger.hour == smaller.hour and
                        bigger.minute > smaller.minute) or (bigger.month == smaller.month and bigger.day == smaller.day and
                        bigger.hour == smaller.hour and bigger.minute == smaller.minute)):
            year_difference = bigger.year - smaller.year
        elif bigger.year > smaller.year:
            year_difference = bigger.year - smaller.year - 1

        if return_as_negatives:
            year_difference *= -1

        month_difference = 0
        if bigger.month > smaller.month and (bigger.day > smaller.day or (
                bigger.day == smaller.day and bigger.hour > smaller.hour) or (
                    bigger.day == smaller.day and bigger.hour == smaller.hour and bigger.minute > smaller.minute) or (
                    bigger.day == smaller.day and bigger.hour == smaller.hour and bigger.minute == smaller.minute)):
            month_difference = bigger.month - smaller.month
        elif bigger.month > smaller.month:
            month_difference = bigger.month - smaller.month - 1
        elif bigger.month <= smaller.month:
            month_difference = 12 - (smaller.month - bigger.month)
            if not (bigger.day > smaller.day or (
                    bigger.day == smaller.day and bigger.hour > smaller.hour) or (
                        bigger.day == smaller.day and bigger.hour == smaller.hour and bigger.minute > smaller.minute) or (
                        bigger.day == smaller.day and bigger.hour == smaller.hour and bigger.minute == smaller.minute)):
                month_difference -= 1
            else:
                if bigger.month == smaller.month:
                    month_difference = 0

        if return_as_negatives:
            month_difference *= -1

        day_difference = 0
        if bigger.day > smaller.day and (bigger.hour > smaller.hour or (
                bigger.hour == smaller.hour and bigger.minute > smaller.minute) or (
                bigger.hour == smaller.hour and bigger.minute == smaller.minute)):
            day_difference = bigger.day - smaller.day
        elif bigger.day > smaller.day:
            day_difference = bigger.day - smaller.day - 1
        elif bigger.day <= smaller.day:
            if bigger.month == 1:
                day_difference = (calendar.monthrange(bigger.year - 1, 12)[1] - smaller.day) + bigger.day
            else:
                day_difference = (calendar.monthrange(bigger.year, bigger.month - 1)[1] - smaller.day) + bigger.day
            if not (bigger.hour > smaller.hour or (
                    bigger.hour == smaller.hour and bigger.minute > smaller.minute) or (
                    bigger.hour == smaller.hour and bigger.minute == smaller.minute)):
                day_difference -= 1
            else:
                if bigger.day == smaller.day:
                    day_difference = 0

        if return_as_negatives:
            day_difference *= -1

        hour_difference = 0
        if bigger.hour > smaller.hour and bigger.minute >= smaller.minute:
            hour_difference = bigger.hour - smaller.hour
        elif bigger.hour > smaller.hour:
            hour_difference = bigger.hour - smaller.hour - 1
        elif bigger.hour <= smaller.hour:
            hour_difference = 24 - (smaller.hour - bigger.hour)
            if not (bigger.minute >= smaller.minute):
                hour_difference -= 1
            else:
                if bigger.hour == smaller.hour:
                    hour_difference = 0
        if hour_difference < 0:
            hour_difference = -hour_difference

        if return_as_negatives:
            hour_difference *= -1

        minute_difference = 0
        if bigger.minute >= smaller.minute:
            minute_difference = bigger.minute - smaller.minute
        else:
            minute_difference = 60 - (smaller.minute - bigger.minute)
        if minute_difference < 0:
            minute_difference = -minute_difference

        if return_as_negatives:
            minute_difference *= -1

        return DateDifference(year_difference, month_difference, day_difference, hour_difference, minute_difference)

    @staticmethod
    def subtract_datestrings(date_string_1: str, date_string_2: str, timezone_1: str = "UTC", timezone_2: str = "UTC"):
        """
        Used if you want to pass in dates and times as strings and/or if you want the difference between two dates to be
        automatically formatted as a string. Input must be formatted as "YYYY-MM-DD HH:MM" (24 hour time) or "YYYY-MM-DD "
        (note the trailing whitespace in the second option). You can also pass in "now" for only one of the two strings
        to use the current date and time. Note that if you do this, you can pass in the timezone, or just use UTC, which
        is the default timezone.

        :param date_string_1: The string that consists of the date to go on the left side of the subtraction,
                              does not contain any timezone info.
        :param date_string_2: The string that consists of the date to go on the right side of the subtraction,
                              does not contain any timezone info.
        :param timezone_1: The timezone to interpret date_string_1 as. Defaults to "UTC".
        :param timezone_2: The timezone to interpret date_string_2 as. Defaults to "UTC".
        :return: A formatted output string consisting of the difference between the two dates given by the date strings.
        """
        hours_and_minutes = True
        if not date_string_1 == "now":
            date_1, hours_and_minutes = simple_parse.parse_raw_date_string(date_string_1)
            date_1 = date_1.replace(tzinfo=tz.gettz(timezone_1))
        else:
            date_1 = datetime.now(tz.gettz(timezone_1))

        date_1 = date_1.replace(microsecond=0)

        if not date_string_2 == "now":
            date_2, compare = simple_parse.parse_raw_date_string(date_string_2)
            date_2 = date_2.replace(tzinfo=tz.gettz(timezone_2))
            if hours_and_minutes:
                hours_and_minutes = compare
        else:
            date_2 = datetime.now(tz.gettz(timezone_2))

        date_2 = date_2.replace(microsecond=0)

        date_difference = DateDifference.subtract_datetimes(date_1, date_2)
        date_difference.hours_and_minutes = hours_and_minutes

        return date_difference

    @staticmethod
    def utc_now():
        """
        Helper method that just gets the current datetime in UTC with tzinfo in place
        :return: the current datetime in UTC with tzinfo in place
        """
        return datetime.now(tz.tzutc())