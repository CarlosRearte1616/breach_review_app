from datetime import datetime

from dateutil.parser import parse


def parse_date(date_string):
    try:
        # check if date_string is not empty or None
        if not date_string or date_string.strip() == "":
            return date_string
        dt = parse(date_string)
        # check if the date is in the future
        if dt > datetime.now():
            # if it's in the future, adjust the year by subtracting 100
            dt = dt.replace(year=dt.year - 100)
        return dt.strftime("%m/%d/%Y")
    except Exception as e:
        print("Invalid date string!: ", f"Error:{e} - {date_string}")
        return date_string + " (Invalid Date Format)"
