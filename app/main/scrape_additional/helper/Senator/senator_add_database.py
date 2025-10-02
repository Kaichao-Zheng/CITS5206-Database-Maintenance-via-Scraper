import json
from .senator_advanced import fetch_senators_combined  
import os
import sys   
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app import db
from app.models import SenatorPeople
   

def senetor_add_to_database():
    
    rows_json = fetch_senators_combined(limit=None, max_workers=10)

    
    for row in rows_json:
        s = SenatorPeople(
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            sector = row.get("sector"),
            state=row.get("state"),
            bussiness_phone=row.get("phones"),
            email=row.get("emails"),
        )
        db.session.add(s)  

    
    db.session.commit()
    print(f"Inserted {len(rows_json)} records into senetor table.")

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
