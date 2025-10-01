from app import GovPeople, db

FIELD_MAP = {
    "Salutation": "salutation",
    "FirstName": "first_name",
    "LastName": "last_name",
    "Organisation": "organization",
    "Position": "role",
    "Gender": "gender",
    "Phone": "business_phone",
    "Email": "email",
    "City": "city",
    "State": "state",
    "Country": "country"
}

def commit_batch(batch):
    for person_data in batch:
        # Try to find an existing record based on name + role
        existing = GovPeople.query.filter_by(
            first_name = person_data.get("FirstName"),
            last_name = person_data.get("LastName"),
            # role = person_data.get("Position") # Optional: Uncomment if role should be part of uniqueness
        ).first()

        if existing:
            for key, value in person_data.items():
                field = FIELD_MAP.get(key)
                if field and hasattr(existing, field):
                    setattr(existing, field, value)
        else:
            # Create new record
            new_person = GovPeople(
                salutation=person_data.get("Salutation"),
                first_name=person_data.get("FirstName"),
                last_name=person_data.get("LastName"),
                organization=person_data.get("Organisation"),
                role=person_data.get("Position"),
                gender=person_data.get("Gender"),
                city=person_data.get("City"),
                state=person_data.get("State"),
                country=person_data.get("Country"),
                business_phone=person_data.get("Phone"),
                mobile_phone=None,
                email=person_data.get("Email"),
                sector=None
            )
            db.session.add(new_person)

    db.session.commit()

def search_database(fname, lname):
    person = GovPeople.query.filter_by(
        first_name=fname,
        last_name=lname
    ).first()

    if person:
        print(f"Found 1 record for {fname} {lname}.")
        return person.as_dict()
    else:
        print(f"No records found for {fname} {lname}.")
        return {}