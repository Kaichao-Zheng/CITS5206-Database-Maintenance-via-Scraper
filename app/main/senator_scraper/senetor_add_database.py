import json
from senetor_revise import fetch_senators_all  
import os
import sys   
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app import db
from app.models import senetor 
   

def senetor_add_to_database():
    
    rows_json = fetch_senators_all(state=None, max_pages=13, limit=None, max_workers=10)

    
    for row in rows_json:
        s = senetor(
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            profile_url=row.get("profile_url"),
            party=row.get("party"),
            state=row.get("state"),
            phones=row.get("phones"),
            emails=row.get("emails"),
            postal_address=row.get("postal_address"),
            source_url=row.get("source_url")
        )
        db.session.add(s)  

    
    db.session.commit()
    print(f"Inserted {len(rows_json)} records into senetor table.")

