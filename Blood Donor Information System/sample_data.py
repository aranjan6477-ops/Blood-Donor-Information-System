"""
sample_data.py - OPTIONAL testing script.

Inserts clearly marked FICTIONAL donors so you can try the application.
These records are for TESTING ONLY and are NOT real blood donors.
Run with:  python sample_data.py
"""
import sqlite3

import database

# name, age, gender, group, mobile, email, city, state, address, last donation, availability
TEST_DONORS = [
    ("Test Donor One (Fictional)", 25, "Male", "O-", "9000000001", "", "Bhopal", "Madhya Pradesh", "", "", "Available"),
    ("Test Donor Two (Fictional)", 30, "Female", "A+", "9000000002", "test2@example.com", "Bhopal", "Madhya Pradesh", "", "2025-01-10", "Available"),
    ("Test Donor Three (Fictional)", 41, "Male", "B+", "9000000003", "", "Indore", "Madhya Pradesh", "", "", "Unavailable"),
    ("Test Donor Four (Fictional)", 22, "Female", "AB+", "9000000004", "", "Indore", "Madhya Pradesh", "", "", "Available"),
    ("Test Donor Five (Fictional)", 35, "Other", "O+", "9000000005", "", "Jabalpur", "Madhya Pradesh", "", "2024-11-05", "Available"),
    ("Test Donor Six (Fictional)", 28, "Male", "A-", "9000000006", "", "Bhopal", "Madhya Pradesh", "", "", "Available"),
    ("Test Donor Seven (Fictional)", 50, "Female", "O+", "9000000007", "", "Bhopal", "Madhya Pradesh", "", "", "Unavailable"),
    ("Test Donor Eight (Fictional)", 19, "Male", "B-", "9000000008", "", "Jabalpur", "Madhya Pradesh", "", "", "Available"),
]


def main():
    database.initialize_database()
    added = skipped = 0
    for donor in TEST_DONORS:
        try:
            database.add_donor(*donor)
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1  # already inserted earlier
    print("These are FICTIONAL test records - not real blood donors.")
    print(f"Added: {added}   Skipped (already present): {skipped}")


if __name__ == "__main__":
    main()
