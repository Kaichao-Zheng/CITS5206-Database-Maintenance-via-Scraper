from app import db
from app.models import GovPeople

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
    for new_person in batch:
        existing = GovPeople.query.filter_by(
            first_name=new_person.first_name,
            last_name=new_person.last_name,
        ).first()

        if existing:
            for field in [
                "salutation", "organization", "role", "gender",
                "city", "state", "country", "business_phone",
                "mobile_phone", "email", "sector"
            ]:
                new_val = getattr(new_person, field, None)
                if new_val:
                    setattr(existing, field, new_val)
        else:
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