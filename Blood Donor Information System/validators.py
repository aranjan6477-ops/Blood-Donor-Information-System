"""
validators.py
Input validation helpers.

Every validator returns a tuple:  (is_valid, value_or_error_message)
 - if is_valid is True  -> the second item is the cleaned value
 - if is_valid is False -> the second item is an error message to show the user
"""
import re
from datetime import datetime, date

VALID_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
VALID_GENDERS = ["Male", "Female", "Other"]
VALID_AVAILABILITY = ["Available", "Unavailable"]

MIN_AGE = 18   # preliminary software filter only - NOT a medical eligibility rule
MAX_AGE = 65

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,59}$")
PLACE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,49}$")


def validate_name(value):
    value = " ".join(value.split())  # remove extra spaces
    if not value:
        return False, "Name cannot be empty."
    if not NAME_PATTERN.match(value):
        return False, "Name must be 2-60 characters (letters, spaces, . ' - only)."
    return True, value.title()


def validate_age(value):
    value = value.strip()
    if not value:
        return False, "Age cannot be empty."
    if not value.isdigit():
        return False, "Age must be a whole number."
    age = int(value)
    if age < MIN_AGE or age > MAX_AGE:
        return False, f"Age must be between {MIN_AGE} and {MAX_AGE} for this system."
    return True, age


def validate_gender(value):
    value = value.strip().lower()
    mapping = {"m": "Male", "male": "Male", "f": "Female", "female": "Female",
               "o": "Other", "other": "Other"}
    if value in mapping:
        return True, mapping[value]
    return False, "Gender must be Male (M), Female (F) or Other (O)."


def validate_blood_group(value):
    value = value.strip().upper().replace(" ", "")
    if value in VALID_BLOOD_GROUPS:
        return True, value
    return False, "Invalid blood group. Use one of: " + ", ".join(VALID_BLOOD_GROUPS)


def validate_mobile(value):
    """Accepts 10-digit Indian mobile numbers (optionally with +91 / 91 / 0 prefix)."""
    cleaned = re.sub(r"[\s-]", "", value)
    if cleaned.startswith("+91"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]
    if not cleaned:
        return False, "Mobile number cannot be empty."
    if not re.fullmatch(r"[6-9]\d{9}", cleaned):
        return False, "Mobile number must be 10 digits and start with 6, 7, 8 or 9."
    return True, cleaned


def validate_email(value):
    """Email is optional: an empty value is accepted."""
    value = value.strip()
    if not value:
        return True, ""
    if len(value) > 100 or not EMAIL_PATTERN.match(value):
        return False, "Invalid email format (example: name@example.com)."
    return True, value.lower()


def validate_place(value, label="City"):
    value = " ".join(value.split())
    if not value:
        return False, f"{label} cannot be empty."
    if not PLACE_PATTERN.match(value):
        return False, f"{label} must be 2-50 characters (letters, spaces, . ' - only)."
    return True, value.title()


def validate_city(value):
    return validate_place(value, "City")


def validate_state(value):
    return validate_place(value, "State")


def validate_address(value):
    """Address is optional."""
    value = " ".join(value.split())
    if len(value) > 150:
        return False, "Address must be at most 150 characters."
    return True, value


def validate_date(value):
    """Optional date in YYYY-MM-DD format; must not be in the future."""
    value = value.strip()
    if not value:
        return True, ""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return False, "Invalid date. Use the format YYYY-MM-DD (example: 2025-01-31)."
    if parsed > date.today():
        return False, "Date cannot be in the future."
    if parsed.year < 1950:
        return False, "Date is too old to be valid."
    return True, parsed.strftime("%Y-%m-%d")


def validate_availability(value):
    value = value.strip().lower()
    if value in ("a", "available", "1", "yes", "y"):
        return True, "Available"
    if value in ("u", "unavailable", "2", "no", "n"):
        return True, "Unavailable"
    return False, "Enter Available (A) or Unavailable (U)."


def validate_donor_id(value):
    value = value.strip()
    if not value.isdigit() or int(value) < 1:
        return False, "Donor ID must be a positive whole number."
    return True, int(value)
