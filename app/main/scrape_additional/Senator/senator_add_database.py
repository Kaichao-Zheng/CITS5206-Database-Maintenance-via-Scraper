import json
from .senator_advanced import fetch_senators_combined  
import os
import sys   
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app import db
from app.models import SenatorPeople
   

from sqlalchemy import delete

def senator_add_to_database():
    rows_json = fetch_senators_combined(limit=None, max_workers=10)

   
    db.session.execute(delete(SenatorPeople))
    db.session.commit()  
   
    n=0
    for row in rows_json:

        existing = SenatorPeople.query.filter_by(profile_url=row.get("profile_url")).first()
        if not existing:
            s = SenatorPeople(
                salutation=row.get("salutations"),
                first_name=row.get("first_name"),
                last_name=row.get("last_name"),
                gender=row.get("gender"),
                role=row.get("position"),
                organization="Parliament of Australia",
                city=row.get("city"),
                state=row.get("state"),
                country ="Australia",
                sector=row.get("sector"),
                business_phone=row.get("phones"),
                email=row.get("emails"),
                profile_url=row.get("source_url")
            )
            db.session.add(s)
            n+=1

    db.session.commit() 
    print(f"Inserted {n} records into senator table.")

def search_database_for_senator(fname, lname):
    person = SenatorPeople.query.filter_by(
        first_name=fname,
        last_name=lname
    ).first()

    if person:
        print(f"Found 1 record for {fname} {lname} in Senator database.")
        return person.as_dict()
    else:
        print(f"No records found for {fname} {lname} in Senator database.")
        return {}
