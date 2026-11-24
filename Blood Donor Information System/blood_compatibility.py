"""
blood_compatibility.py
Simplified red blood cell (RBC) donor -> recipient compatibility table.
"""

# donor blood group -> list of recipient groups that can receive from them
DONOR_TO_RECIPIENTS = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],
}

DISCLAIMER = (
    "NOTE: This is a simplified red blood cell compatibility reference only.\n"
    "Actual transfusion decisions must be made by qualified medical professionals\n"
    "after proper blood-bank testing and cross-matching."
)


def get_compatible_donor_groups(recipient_group):
    """Return the list of donor blood groups that can give to the recipient group."""
    return [donor for donor, recipients in DONOR_TO_RECIPIENTS.items()
            if recipient_group in recipients]
