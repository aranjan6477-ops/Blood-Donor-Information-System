# Blood Donor Information System

A menu-driven, terminal-based Python 3 + SQLite3 application for registering and searching blood donors. College minor project.

## Project Description
The system stores donor details in a local SQLite database (`blood_donor.db`) and lets users register, search, update, delete and analyse donor records, including a simplified blood group compatibility checker. It runs fully offline in the terminal - no web browser, server, GUI or internet needed.

## Objectives
- Register blood donors and store their data locally.
- Search donors by blood group, city and donor ID.
- Update and delete donor records safely (with confirmation).
- Identify potential donors using blood group compatibility.
- Maintain donor availability information and show statistics.

## Features
1. Register New Donor (auto ID, full validation, duplicate-mobile check)
2. View All Donors (table)
3. Search by Blood Group (available donors; optional unavailable list)
4. Search by City (case-insensitive, partial match)
5. Search by Donor ID (full record)
6. Update Donor Information (Enter keeps old value, `-` clears optional fields)
7. Delete Donor Record (shows record, asks confirmation)
8. Blood Group Compatibility Checker (with medical disclaimer)
9. View Available Donors (filter by blood group and city)
10. System Statistics (totals, per group, per city, most common group)
11. Exit

Tip: type `cancel` at any prompt to return to the main menu.

## Technologies Used
Python 3, `sqlite3`, `re`, `datetime`, `os`, `contextlib` (standard library only).

## Project Folder Structure
```
Blood_Donor_Information_System/
├── main.py                  # entry point + main menu loop
├── database.py              # all SQLite operations
├── donor_operations.py      # menu operations (input/output)
├── blood_compatibility.py   # compatibility table + disclaimer
├── validators.py            # input validation functions
├── sample_data.py           # OPTIONAL fictional test data
├── requirements.txt         # no third-party packages needed
├── README.md
├── VIVA_AND_TESTING.md      # testing checklist, errors, viva Q&A
└── blood_donor.db           # created automatically on first run
```

## Database Information
Database file: `blood_donor.db`, table `donors`:

| Column | Type |
|---|---|
| donor_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| full_name | TEXT NOT NULL |
| age | INTEGER NOT NULL |
| gender | TEXT NOT NULL |
| blood_group | TEXT NOT NULL |
| mobile | TEXT NOT NULL UNIQUE |
| email | TEXT |
| city | TEXT NOT NULL |
| state | TEXT NOT NULL |
| address | TEXT |
| last_donation_date | TEXT (YYYY-MM-DD) |
| availability | TEXT NOT NULL DEFAULT 'Available' |
| created_at | TEXT NOT NULL |

All queries are parameterized to prevent SQL injection. Only the data listed above is stored.

## Installation
1. Install Python 3 from https://www.python.org (tick "Add Python to PATH" on Windows).
2. Extract the zip and open the `Blood_Donor_Information_System` folder in Command Prompt, PowerShell or the VS Code terminal.
3. No `pip install` is needed.

## How to Run
```
python main.py
```
(On some systems use `python3 main.py` or `py main.py`.) The database is created automatically.

Optional - load FICTIONAL test donors (not real people; for testing only):
```
python sample_data.py
```

## Sample Terminal Output
```
==================================================
          BLOOD DONOR INFORMATION SYSTEM
==================================================
 1. Register New Donor
 ...
11. Exit
==================================================
Enter your choice: 2

ID   Name                    Age  Group  City            Mobile      Status
------------------------------------------------------------------------------
1    Test Donor One (Fictio  25   O-     Bhopal          9000000001  [+] Available
3    Test Donor Three (Fict  41   B+     Indore          9000000003  [-] Unavailable
------------------------------------------------------------------------------
Total records: 2
```

## Example Workflows
- **Register:** option 1 -> enter details -> "Donor registered successfully! Donor ID: N".
- **Find blood urgently:** option 8 -> enter recipient group -> see compatible groups and available donors with city and mobile.
- **Mark donor unavailable:** option 6 -> enter ID -> Enter to keep fields -> type `U` at Availability.
- **Remove a record:** option 7 -> ID -> review details -> type `yes`.

## Limitations
- Single-user, local database; no login or encryption of stored data.
- Age 18-65 is only a preliminary filter, NOT a medical eligibility check.
- Compatibility covers simplified red-cell rules only; actual transfusion decisions need qualified medical professionals and blood-bank testing.
- Mobile validation follows the Indian 10-digit format.
- Donor data is personal information; do not use test data as real donors, and protect the database file.

## Future Enhancements
- Password-protected admin login and encrypted storage.
- Automatic availability based on 90-day donation gap.
- Export to CSV / PDF, backup and restore.
- Plasma/platelet compatibility, SMS/email alerts, GUI or web version.
