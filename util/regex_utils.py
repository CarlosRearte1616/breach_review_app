import re
from datetime import datetime


def is_bank_account_number(s):
    # Here are some regex patterns based on the examples given:
    patterns = [
        r'^\d{10,12}$',  # US (10-12 digits)
        r'^\d{8}$',  # UK (8 digits)
        r'^\d{5,12}$',  # Canada (5-12 digits)
        r'^\d{6,10}$',  # Australia (6-10 digits)
        r'^\d{10}$',  # Germany (10 digits)
        r'^\d{11}( \d{2})?$',  # France (11 digits, possibly followed by a 2-digit key)
        r'^\d{9,18}$',  # India (9-18 digits)
        r'^\d{7}$',  # Japan (7 digits)
        r'^\d{10}$',  # Brazil (10 digits)
        r'^\d{11}$',  # South Africa (11 digits)
        r'^\d{9,10}$',  # Netherlands (9-10 digits)
        r'^\d{16,19}$',  # China (16-19 digits)
        r'^\d{20}$',  # Spain, Russia (20 digits)
        r'^\d{12}$',  # Italy (12 digits)
    ]

    for pattern in patterns:
        if re.fullmatch(pattern, s):
            return True

    return False


def could_be_address(address):
    pattern = r"^(.*?)[, ]+(.*?)[, ]+(.*?)[, ]+(\d{5}(?:-\d{4})?)$"
    return bool(re.match(pattern, address, re.IGNORECASE))


def could_be_credit_card(s):
    # Remove spaces and hyphens
    s = re.sub(r'[ -]', '', s)

    # Check if the remaining characters are all digits and the length is within the expected range
    if not re.fullmatch(r'\d{13,19}', s):
        return False

    # Check for known card issuer prefixes
    if re.fullmatch(r'4(\d{12}|\d{15})', s):  # Visa
        return True
    elif re.fullmatch(r'5[1-5]\d{14}', s):  # MasterCard
        return True
    elif re.fullmatch(r'3[47]\d{13}', s):  # American Express
        return True
    elif re.fullmatch(r'(6011\d{12}|65\d{14})', s):  # Discover
        return True

    # If it's not one of the known prefixes, it could still be a credit card number
    # (as there are many other issuers not covered here)
    return True


def could_be_routing_number(s):
    # Check if the string is exactly nine digits
    if not re.fullmatch(r'\d{9}', s):
        return False

    # Implement the checksum validation
    digits = [int(ch) for ch in s]
    checksum = (3 * (digits[0] + digits[3] + digits[6]) +
                7 * (digits[1] + digits[4] + digits[7]) +
                (digits[2] + digits[5] + digits[8])) % 10

    return checksum == 0


def could_be_ssn(s):
    return bool(re.fullmatch(r'\d{3}-\d{2}-\d{4}', s))


def could_be_name(s):
    return bool(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ',’. -]{1,100}(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ',’. -]{1,100})*", s))


def is_date_of_birth(input_string):
    date_formats = ["%m/%d/%y", "%d/%m/%y", "%m-%d-%Y", "%d-%m-%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%y", "%d/%m/%Y",
                    "%m/%d/%Y", "%Y/%m/%d",
                    "%B %d, %Y", "%B %d. %Y"]

    date = None
    # Try to parse the date using each format
    for fmt in date_formats:
        try:
            date = datetime.strptime(input_string, fmt)
            # If the parsed year is in the future, adjust it by 100 years.
            if date.year > datetime.now().year:
                date = date.replace(year=date.year - 100)
            # If the parsing succeeds, break the loop
            break
        except ValueError:
            pass

    if date is None:
        # If no format matched, print an error and return False
        print("Invalid date format. Please provide a valid date.")
        result = False
    else:
        # Get the current year
        current_year = datetime.now().year

        # Check that the date is within a reasonable range
        if 1910 <= date.year <= current_year:
            result = True
        else:
            print("Year must be between 1910 and the current year.")
            result = False

    return result


def is_drivers_license(license_number):
    formats = {
        'Alabama': r'^\d{1,8}$',
        'Alaska': r'^\d{1,7}$',
        'Arizona': r'^(?:[A-Za-z]\d{8}|\d{9})$',
        'Arkansas': r'^\d{4,9}$',
        'California': r'^[A-Za-z]\d{7}$',
        'Colorado': r'^(?:\d{9}|[A-Za-z]\d{3,6}|[A-Za-z]{2}\d{2,5})$',
        'Connecticut': r'^\d{9}$',
        'Delaware': r'^\d{1,7}$',
        'District of Columbia': r'^\d{7,9}$',
        'Florida': r'^[A-Za-z]\d{12}$',
        'Georgia': r'^\d{7,9}$',
        'Hawaii': r'^(?:[A-Za-z]\d{8}|\d{9})$',
        'Idaho': r'^(?:[A-Za-z]{2}\d{6}[A-Za-z]|\d{9})$',
        'Illinois': r'^[A-Za-z]\d{11,12}$',
        'Indiana': r'^(?:[A-Za-z]\d{9}|\d{9,10})$',
        'Iowa': r'^(?:\d{9}|\d{3}[A-Za-z]{2}\d{4})$',
        'Kansas': r'^(?:[A-Za-z]\d[A-Za-z]\d[A-Za-z]|[A-Za-z]\d{8}|\d{9})$',
        'Kentucky': r'^(?:[A-Za-z]\d{8,9}|\d{9})$',
        'Louisiana': r'^\d{1,9}$',
        'Maine': r'^(?:\d{7}|[A-Za-z]\d{7}|\d{8})$',
        'Maryland': r'^[A-Za-z]\d{12}$',
        'Massachusetts': r'^(?:[A-Za-z]\d{8}|\d{9})$',
        'Michigan': r'^[A-Za-z]\d{10,12}$',
        'Minnesota': r'^[A-Za-z]\d{12}$',
        'Mississippi': r'^\d{9}$',
        'Missouri': r'^(?:\d{3}[A-Za-z]\d{6}|[A-Za-z]\d{5,9}|[A-Za-z]\d{6}R|\d{8}[A-Za-z]{2}|\d{9}[A-Za-z]|\d{9})$',
        'Montana': r'^(?:[A-Za-z]\d{8}|\d{9,14})$',
        'Nebraska': r'^[A-Za-z]\d{6,8}$',
        'Nevada': r'^(?:\d{9,10}|\d{12}|X\d{8})$',
        'New Hampshire': r'^\d{2}[A-Za-z]{3}\d{5}$',
        'New Jersey': r'^[A-Za-z]\d{14}$',
        'New Mexico': r'^\d{8,9}$',
        'New York': r'^(?:[A-Za-z]\d{7}|[A-Za-z]\d{18}|\d{8,9}|\d{16}|[A-Za-z]{8})$',
        'North Carolina': r'^\d{1,12}$',
        'North Dakota': r'^(?:[A-Za-z]{3}\d{6}|\d{9})$',
        'Ohio': r'^(?:[A-Za-z]\d{4,8}|[A-Za-z]{2}\d{3,7}|\d{8})$',
        'Oklahoma': r'^(?:[A-Za-z]\d{9}|\d{9})$',
        'Oregon': r'^\d{1,9}$',
        'Pennsylvania': r'^\d{8}$',
        'Rhode Island': r'^(?:\d{7}|[A-Za-z]\d{6})$',
        'South Carolina': r'^\d{5,11}$',
        'South Dakota': r'^\d{6,10}$',
        'Tennessee': r'^\d{7,9}$',
        'Texas': r'^\d{7,8}$',
        'Utah': r'^\d{4,10}$',
        'Vermont': r'^(?:\d{8}|\d{7}A)$',
        'Virginia': r'^(?:[A-Za-z]\d{8,11}|\d{9})$',
        'Washington': r'^[A-Za-z]{1,7}\w{5,11}$',
        'West Virginia': r'^(?:\d{7}|[A-Za-z]{1,2}\d{5,6})$',
        'Wisconsin': r'^[A-Za-z]\d{13}$',
        'Wyoming': r'^\d{9,10}$'
    }
    # Check if the license number matches any of the known formats
    for state, pattern in formats.items():
        if re.fullmatch(pattern, license_number):
            return True
        else:
            return False


def is_passport_number(input_string):
    # Matches 8 or 9 alphanumeric characters
    match = re.fullmatch(r"[A-Za-z0-9]{8,9}", input_string)
    return bool(match)


def is_medical_record_number(input_string):
    # Matches an alphanumeric string with a length of up to 10
    pattern = r'^[A-Za-z0-9\-]{4,16}$'
    return bool(re.match(pattern, input_string))


def is_credit_card_security_code(input_string):
    # Matches a 3-digit number for Visa and Mastercard or 4-digit number for American Express
    match = re.fullmatch(r"\d{3,4}", input_string)
    return bool(match)


def is_expiration_date(input_string):
    # Matches dates in format MM/YY
    match = re.fullmatch(r"(0[1-9]|1[0-2])/(0[0-9]|[12]\d|3[0-1])", input_string)
    return bool(match)


def is_email(input_string):
    # Matches email addresses
    match = re.fullmatch(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", input_string)
    return bool(match)


def is_account_username(input_string):
    # Matches a string of alphanumeric characters with a length of 4 to 20
    match = re.fullmatch(r"[A-Za-z0-9_]{4,20}", input_string)
    return bool(match)


def is_valid_password(password):
    # Check length (at least 8 characters)
    if len(password) < 8:
        return False

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False

    # All checks passed, the password is valid
    return True
