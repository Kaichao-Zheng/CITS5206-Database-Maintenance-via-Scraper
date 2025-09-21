import time
from helper.ip_scraping import scrape_https_proxies 
from helper.profile_url_scrape import scrape_linkedin_people_search
from app import db
from app.models import IP, People, Profile
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify,send_file
from sqlalchemy.exc import SQLAlchemyError
from app.main.scraping import sc
from flask_login import current_user, login_user,logout_user,login_required
import os

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def get_people_names():
    # get all record from People and make it a list
    session = db.session
    people_records = session.query(People).all()  
    names = [f"{person.first_name} {person.last_name}" for person in people_records]
    session.close()
    return names

@sc.route('/scrape_and_store_proxies', methods=['GET'])
@login_required
def scrape_and_store_proxies():
    try:
       
        https_proxies = scrape_https_proxies()

        session = db.session

        for proxy in https_proxies:
           
            address, port = proxy.split(":")
            port = int(port) 

            
            ip_entry = IP(
                address=address,
                port=port,
                type="https",
                source="free-proxy-list",
                is_expired=False  
            )

            session.add(ip_entry)

        
        session.commit()

        
        return jsonify({"message": "Proxies successfully scraped and stored."}), 200

    except SQLAlchemyError as e:
        session.rollback()  
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@sc.route('/scrape_profile_url', methods=['GET'])
def scrape_linkedin():
    try:
        # get names list
        names = get_people_names()

        # execute scrape_linkedin_people_search 
        cookies_file = "my_linkedin_cookies.json"  # define name of cookies file
        results = scrape_linkedin_people_search(names, LINKEDIN_EMAIL, LINKEDIN_PASSWORD, cookies_file)
        for name, url in results.items():
            # Split name into first_name and last_name
            name_parts = name.split(" ")
            if len(name_parts) == 2:
                first_name, last_name = name_parts
            else:
                first_name = name_parts[0]
                last_name = ""  # In case there's no last name (e.g., only one part in the name)
            
            # Create a new Profile object and save to DB
            new_profile = Profile(first_name=first_name, last_name=last_name, url=url)
            db.session.add(new_profile)

        # Commit the changes to the database
        db.session.commit()

        
        return jsonify({"message": "Scraping successful", "results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    


    