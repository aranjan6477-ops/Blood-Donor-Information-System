"""
donor_operations.py
Menu operations: they talk to the user (input/print) and call database.py for storage.
"""
import sqlite3
from datetime import datetime, date

import database
import validators
from blood_compatibility import get_compatible_donor_groups, DISCLAIMER

LINE = "=" * 78
THIN = "-" * 78


class CancelOperation(Exception):
    """Raised when the user types 'cancel' at any prompt."""


# ---------------------------------------------------------------- helpers
def ask(prompt, validator, current=None, clearable=False):
    """Keep asking until the validator accepts the input.
    current   : if given (update mode), pressing Enter keeps this value.
    clearable : if True (update mode, optional fields), typing '-' clears the value.
    """
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            raise CancelOperation()
        if current is not None and raw == "":
            return current
        if clearable and raw == "-":
            return ""
        is_valid, result = validator(raw)
        if is_valid:
            return result
        print(f"  [ERROR] {result}")


def make_mobile_validator(exclude_id=None):
    """Validator that also rejects mobile numbers already used by another donor."""
    def validator(value):
        is_valid, result = validators.validate_mobile(value)
        if not is_valid:
            return False, result
        existing = database.get_donor_by_mobile(result)
        if existing and existing["donor_id"] != exclude_id:
            return False, (f"This mobile number is already registered "
                           f"(Donor ID {existing['donor_id']}).")
        return True, result
    return validator


def print_header(title):
    print("\n" + LINE)
    print(title.center(78))
    print(LINE)


def status_text(availability):
    return "[+] Available" if availability == "Available" else "[-] Unavailable"


def print_donor_table(rows):
    """Print donors in a table: ID, Name, Age, Blood Group, City, Mobile, Status."""
    header = (f"{'ID':<5}{'Name':<24}{'Age':<5}{'Group':<7}"
              f"{'City':<16}{'Mobile':<12}{'Status'}")
    print(header)
    print(THIN)
    for row in rows:
        print(f"{row['donor_id']:<5}{row['full_name'][:22]:<24}{row['age']:<5}"
              f"{row['blood_group']:<7}{row['city'][:14]:<16}{row['mobile']:<12}"
              f"{status_text(row['availability'])}")
    print(THIN)
    print(f"Total records: {len(rows)}")


def print_donor_details(row):
    print(THIN)
    print(f"  Donor ID           : {row['donor_id']}")
    print(f"  Full Name          : {row['full_name']}")
    print(f"  Age                : {row['age']}")
    print(f"  Gender             : {row['gender']}")
    print(f"  Blood Group        : {row['blood_group']}")
    print(f"  Mobile             : {row['mobile']}")
    print(f"  Email              : {row['email'] or 'Not provided'}")
    print(f"  City               : {row['city']}")
    print(f"  State              : {row['state']}")
    print(f"  Address            : {row['address'] or 'Not provided'}")
    print(f"  Last Donation Date : {row['last_donation_date'] or 'Not provided'}")
    print(f"  Availability       : {status_text(row['availability'])}")
    print(f"  Registered On      : {row['created_at']}")
    print(THIN)


def days_since(date_text):
    """Days since a YYYY-MM-DD date (used for a friendly reminder only)."""
    return (date.today() - datetime.strptime(date_text, "%Y-%m-%d").date()).days


def ask_existing_donor(prompt="Enter Donor ID: "):
    """Ask for a donor ID and return the record (or None if not found)."""
    donor_id = ask(prompt, validators.validate_donor_id)
    donor = database.get_donor_by_id(donor_id)
    if donor is None:
        print(f"  [ERROR] No donor found with ID {donor_id}.")
    return donor


# ---------------------------------------------------------------- 1. register
def register_donor():
    print_header("REGISTER NEW DONOR")
    print("(Type 'cancel' at any prompt to return to the menu)\n")
    full_name = ask("Full Name                          : ", validators.validate_name)
    age = ask(f"Age ({validators.MIN_AGE}-{validators.MAX_AGE})                      : ",
              validators.validate_age)
    gender = ask("Gender (Male/Female/Other or M/F/O) : ", validators.validate_gender)
    blood_group = ask("Blood Group (A+,A-,B+,B-,AB+,AB-,O+,O-): ",
                      validators.validate_blood_group)
    mobile = ask("Mobile Number (10 digits)           : ", make_mobile_validator())
    email = ask("Email (optional, Enter to skip)     : ", validators.validate_email)
    city = ask("City                               : ", validators.validate_city)
    state = ask("State                              : ", validators.validate_state)
    address = ask("Address (optional, Enter to skip)   : ", validators.validate_address)
    last_date = ask("Last Donation Date YYYY-MM-DD (optional): ", validators.validate_date)
    availability = ask("Availability (Available/Unavailable or A/U): ",
                       validators.validate_availability)

    try:
        donor_id = database.add_donor(full_name, age, gender, blood_group, mobile, email,
                                      city, state, address, last_date, availability)
    except sqlite3.IntegrityError:
        print("\n  [ERROR] This mobile number is already registered. Donor not saved.")
        return
    print(f"\n  [SUCCESS] Donor registered successfully! Donor ID: {donor_id}")
    if last_date and days_since(last_date) < 90:
        print("  [INFO] Last donation was less than 90 days ago. Please confirm the donor's "
              "availability with the blood bank.")


# ---------------------------------------------------------------- 2. view all
def view_all_donors():
    print_header("ALL REGISTERED DONORS")
    donors = database.get_all_donors()
    if not donors:
        print("  No donors are registered yet. Use option 1 to register a donor.")
        return
    print_donor_table(donors)


# ---------------------------------------------------------------- 3. by blood group
def search_by_blood_group():
    print_header("SEARCH DONOR BY BLOOD GROUP")
    blood_group = ask("Enter blood group (e.g. O+): ", validators.validate_blood_group)
    available = database.search_donors(blood_groups=[blood_group], availability="Available")
    print(f"\nAvailable donors with blood group {blood_group}:")
    if available:
        print_donor_table(available)
    else:
        print(f"  No available donors found for blood group {blood_group}.")

    answer = input("\nAlso show UNAVAILABLE donors of this group? (y/n): ").strip().lower()
    if answer in ("y", "yes"):
        unavailable = database.search_donors(blood_groups=[blood_group],
                                             availability="Unavailable")
        print(f"\nUnavailable donors with blood group {blood_group}:")
        if unavailable:
            print_donor_table(unavailable)
        else:
            print("  No unavailable donors found.")


# ---------------------------------------------------------------- 4. by city
def search_by_city():
    print_header("SEARCH DONOR BY CITY")
    city = input("Enter city name: ").strip()
    if city.lower() == "cancel":
        raise CancelOperation()
    if not city:
        print("  [ERROR] City name cannot be empty.")
        return
    donors = database.search_donors(city=city)
    if not donors:
        print(f"\n  No donors found in '{city}'.")
        return
    print(f"\nDonors matching city '{city}':")
    print_donor_table(donors)


# ---------------------------------------------------------------- 5. by id
def search_by_id():
    print_header("SEARCH DONOR BY ID")
    donor = ask_existing_donor()
    if donor:
        print_donor_details(donor)


# ---------------------------------------------------------------- 6. update
def update_donor_information():
    print_header("UPDATE DONOR INFORMATION")
    print("(Type 'cancel' at any prompt to return to the menu)\n")
    donor = ask_existing_donor()
    if donor is None:
        return
    print("\nCurrent record:")
    print_donor_details(donor)
    print("Press Enter to keep the current value. For optional fields type '-' to clear.\n")

    def current(column):
        return donor[column] if donor[column] is not None else ""

    new_values = {}
    new_values["full_name"] = ask(f"Full Name [{donor['full_name']}]: ",
                                  validators.validate_name, donor["full_name"])
    new_values["age"] = ask(f"Age [{donor['age']}]: ", validators.validate_age, donor["age"])
    new_values["gender"] = ask(f"Gender [{donor['gender']}]: ",
                               validators.validate_gender, donor["gender"])
    new_values["blood_group"] = ask(f"Blood Group [{donor['blood_group']}]: ",
                                    validators.validate_blood_group, donor["blood_group"])
    new_values["mobile"] = ask(f"Mobile [{donor['mobile']}]: ",
                               make_mobile_validator(donor["donor_id"]), donor["mobile"])
    new_values["email"] = ask(f"Email [{current('email') or 'none'}]: ",
                              validators.validate_email, current("email") or None,
                              clearable=True) or ""
    new_values["city"] = ask(f"City [{donor['city']}]: ", validators.validate_city, donor["city"])
    new_values["state"] = ask(f"State [{donor['state']}]: ",
                              validators.validate_state, donor["state"])
    new_values["address"] = ask(f"Address [{current('address') or 'none'}]: ",
                                validators.validate_address, current("address") or None,
                                clearable=True) or ""
    new_values["last_donation_date"] = ask(
        f"Last Donation Date [{current('last_donation_date') or 'none'}]: ",
        validators.validate_date, current("last_donation_date") or None,
        clearable=True) or ""
    new_values["availability"] = ask(f"Availability [{donor['availability']}]: ",
                                     validators.validate_availability, donor["availability"])

    # Only save the fields that really changed
    changes = {col: val for col, val in new_values.items() if val != (donor[col] or "")}
    if not changes:
        print("\n  [INFO] No changes were made.")
        return
    try:
        database.update_donor(donor["donor_id"], changes)
    except sqlite3.IntegrityError:
        print("\n  [ERROR] That mobile number belongs to another donor. Nothing was saved.")
        return
    print(f"\n  [SUCCESS] Donor {donor['donor_id']} updated. "
          f"Fields changed: {', '.join(changes)}")


# ---------------------------------------------------------------- 7. delete
def delete_donor_record():
    print_header("DELETE DONOR RECORD")
    donor = ask_existing_donor()
    if donor is None:
        return
    print_donor_details(donor)
    answer = input("Are you sure you want to permanently delete this donor? (yes/no): ")
    if answer.strip().lower() in ("yes", "y"):
        if database.delete_donor(donor["donor_id"]):
            print(f"\n  [SUCCESS] Donor {donor['donor_id']} deleted.")
        else:
            print("\n  [ERROR] Record could not be deleted.")
    else:
        print("\n  [INFO] Deletion cancelled. The record was not changed.")


# ---------------------------------------------------------------- 8. compatibility
def check_compatibility():
    print_header("BLOOD GROUP COMPATIBILITY CHECKER")
    recipient = ask("Enter RECIPIENT blood group: ", validators.validate_blood_group)
    compatible_groups = get_compatible_donor_groups(recipient)
    print(f"\nCompatible donor blood groups for recipient group {recipient}:")
    print("  " + ", ".join(compatible_groups))
    donors = database.search_donors(blood_groups=compatible_groups, availability="Available")
    print(f"\nAvailable registered donors with compatible blood groups:")
    if donors:
        print_donor_table(donors)
    else:
        print("  No available registered donors found with compatible blood groups.")
    print("\n" + DISCLAIMER)


# ---------------------------------------------------------------- 9. available donors
def view_available_donors():
    print_header("AVAILABLE DONORS")
    print("Optional filters - press Enter to skip a filter.")
    blood_group = ask("Filter by blood group: ",
                      lambda v: (True, "") if not v.strip() else validators.validate_blood_group(v))
    city = input("Filter by city       : ").strip()
    donors = database.search_donors(blood_groups=[blood_group] if blood_group else None,
                                    city=city or None, availability="Available")
    if not donors:
        print("\n  No available donors found for the selected filters.")
        return
    print()
    print_donor_table(donors)


# ---------------------------------------------------------------- 10. statistics
def display_statistics():
    print_header("SYSTEM STATISTICS")
    stats = database.get_statistics()
    if stats["total"] == 0:
        print("  The database is empty. Register donors to see statistics.")
        return
    print(f"  Total registered donors : {stats['total']}")
    print(f"  Available donors        : {stats['available']}")
    print(f"  Unavailable donors      : {stats['unavailable']}")
    print("\n  Donors by blood group:")
    for group, count in stats["by_group"]:
        print(f"    {group:<5}: {count} {'#' * count}")
    print("\n  Donors by city:")
    for city, count in stats["by_city"]:
        print(f"    {city:<20}: {count}")
    top_count = stats["by_group"][0][1]
    top_groups = [g for g, c in stats["by_group"] if c == top_count]
    print(f"\n  Most commonly registered blood group: {', '.join(top_groups)} "
          f"({top_count} donor{'s' if top_count != 1 else ''})")
