"""
database.py
All SQLite3 operations live here (no menu / input logic).
All queries use parameters (?) to prevent SQL injection.
"""
import os
import sqlite3
from contextlib import closing
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# The environment variable is only used by automated tests; normally the default is used.
DB_PATH = os.environ.get("BLOOD_DONOR_DB", os.path.join(BASE_DIR, "blood_donor.db"))

# Only these columns may be changed by update_donor() (protects the dynamic UPDATE query)
UPDATABLE_COLUMNS = {
    "full_name", "age", "gender", "blood_group", "mobile", "email",
    "city", "state", "address", "last_donation_date", "availability",
}


def get_connection():
    """Open a connection; rows can be read like dictionaries (row['city'])."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create the database file and donors table on first run."""
    with closing(get_connection()) as conn:
        with conn:  # commits automatically
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS donors (
                    donor_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name          TEXT NOT NULL,
                    age                INTEGER NOT NULL,
                    gender             TEXT NOT NULL,
                    blood_group        TEXT NOT NULL,
                    mobile             TEXT NOT NULL UNIQUE,
                    email              TEXT,
                    city               TEXT NOT NULL,
                    state              TEXT NOT NULL,
                    address            TEXT,
                    last_donation_date TEXT,
                    availability       TEXT NOT NULL DEFAULT 'Available',
                    created_at         TEXT NOT NULL
                )
                """
            )


def add_donor(full_name, age, gender, blood_group, mobile, email, city, state,
              address, last_donation_date, availability):
    """Insert a donor and return the new donor_id.
    Raises sqlite3.IntegrityError if the mobile number already exists."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO donors (full_name, age, gender, blood_group, mobile, email,
                                    city, state, address, last_donation_date,
                                    availability, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (full_name, age, gender, blood_group, mobile, email, city, state,
                 address, last_donation_date, availability, created_at),
            )
            return cursor.lastrowid


def get_all_donors():
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM donors ORDER BY donor_id").fetchall()


def get_donor_by_id(donor_id):
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM donors WHERE donor_id = ?", (donor_id,)).fetchone()


def get_donor_by_mobile(mobile):
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM donors WHERE mobile = ?", (mobile,)).fetchone()


def search_donors(blood_groups=None, city=None, availability=None):
    """Flexible search. Every argument is optional.
    blood_groups : list of blood groups (matches any of them)
    city         : case-insensitive partial match
    availability : 'Available' or 'Unavailable'
    """
    query = "SELECT * FROM donors WHERE 1=1"
    params = []
    if blood_groups:
        # Only '?' placeholders are inserted into the SQL text; the values stay parameters.
        placeholders = ",".join(["?"] * len(blood_groups))
        query += f" AND blood_group IN ({placeholders})"
        params.extend(blood_groups)
    if city:
        query += " AND instr(lower(city), lower(?)) > 0"
        params.append(city)
    if availability:
        query += " AND availability = ?"
        params.append(availability)
    query += " ORDER BY full_name COLLATE NOCASE"
    with closing(get_connection()) as conn:
        return conn.execute(query, params).fetchall()


def update_donor(donor_id, updates):
    """Update the given {column: value} pairs. Returns True if a row was changed.
    Raises sqlite3.IntegrityError on duplicate mobile numbers."""
    if not updates:
        return False
    for column in updates:
        if column not in UPDATABLE_COLUMNS:
            raise ValueError(f"Column '{column}' cannot be updated.")
    set_clause = ", ".join(f"{column} = ?" for column in updates)  # column names are whitelisted
    params = list(updates.values()) + [donor_id]
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(f"UPDATE donors SET {set_clause} WHERE donor_id = ?", params)
            return cursor.rowcount > 0


def delete_donor(donor_id):
    """Delete a donor. Returns True if a row was deleted."""
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM donors WHERE donor_id = ?", (donor_id,))
            return cursor.rowcount > 0


def get_statistics():
    """Return a dictionary with all statistics shown in menu option 10."""
    with closing(get_connection()) as conn:
        total = conn.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
        available = conn.execute(
            "SELECT COUNT(*) FROM donors WHERE availability = 'Available'").fetchone()[0]
        by_group = conn.execute(
            "SELECT blood_group, COUNT(*) AS total FROM donors "
            "GROUP BY blood_group ORDER BY total DESC, blood_group").fetchall()
        by_city = conn.execute(
            "SELECT city, COUNT(*) AS total FROM donors "
            "GROUP BY city COLLATE NOCASE ORDER BY total DESC, city").fetchall()
    return {
        "total": total,
        "available": available,
        "unavailable": total - available,
        "by_group": [(row["blood_group"], row["total"]) for row in by_group],
        "by_city": [(row["city"], row["total"]) for row in by_city],
    }
