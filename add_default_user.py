from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash
from app import db, create_app
from app.models import User

load_dotenv()  

app = create_app()
with app.app_context():
    password_plain = os.environ.get("DEFAULT_PASSWORD")
    
    hashed_password = generate_password_hash(password_plain)
    new_user = User(username="admin", password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    print("User added successfully!")
