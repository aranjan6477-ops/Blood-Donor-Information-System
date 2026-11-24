import sqlite3
import database
import donor_operations as ops

MENU = """
==================================================
          BLOOD DONOR INFORMATION SYSTEM
==================================================
 1. Register New Donor
 2. View All Donors
 3. Search Donor by Blood Group
 4. Search Donor by City
 5. Search Donor by Donor ID
 6. Update Donor Information
 7. Delete Donor Record
 8. Check Blood Group Compatibility
 9. View Available Donors
10. Display System Statistics
11. Exit
=================================================="""

# menu choice -> function
ACTIONS = {
    "1": ops.register_donor,
    "2": ops.view_all_donors,
    "3": ops.search_by_blood_group,
    "4": ops.search_by_city,
    "5": ops.search_by_id,
    "6": ops.update_donor_information,
    "7": ops.delete_donor_record,
    "8": ops.check_compatibility,
    "9": ops.view_available_donors,
    "10": ops.display_statistics,
}


def main():
    try:
        database.initialize_database()
    except sqlite3.Error as error:
        print(f"[ERROR] Could not initialize the database: {error}")
        return

    try:
        while True:
            print(MENU)
            choice = input("Enter your choice: ").strip()
            if choice == "11":
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("\n  [ERROR] Invalid choice. Please enter a number from 1 to 11.")
                continue
            try:
                action()
            except ops.CancelOperation:
                print("\n  [INFO] Operation cancelled.")
            except sqlite3.Error as error:
                print(f"\n  [ERROR] Database problem: {error}")
            input("\nPress Enter to return to the main menu...")
    except (KeyboardInterrupt, EOFError):
        print()  # user pressed Ctrl+C / Ctrl+D or input ended

    print("\n" + "=" * 50)
    print("  Thank you for using the Blood Donor")
    print("  Information System. Every donation can save")
    print("  a life. Goodbye!")
    print("=" * 50)


if __name__ == "__main__":
    main()
