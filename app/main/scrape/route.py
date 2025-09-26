import time
from .helper.ip_scraping import scrape_https_proxies 
from .helper.profile_url_scrape import scrape_linkedin_people_search
from app import db
from app.models import IP, People, Profile
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify,send_file
from sqlalchemy.exc import SQLAlchemyError
from app.main.scraping import sc
from flask_login import current_user, login_user,logout_user,login_required
import os
import sqlalchemy as sa
from .helper.scrape_information import scrape_profiles

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def conditional_get_people_names_for_url_searching(number: int):
    session = db.session

    
    people_records = session.query(People)

    result = []
    for person in people_records:
        if person.linkedin:
            print(f"skip {person.first_name} {person.last_name} cause the url already exists")
            continue
        result.append(f"{person.first_name} {person.last_name}")
        if len(result) >= number:
            break

    session.close()
    return result

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
        number = request.args.get('number', default=10, type=int)

        # Get names
        names = conditional_get_people_names_for_url_searching(number)

        # Execute scraping
        cookies_file = "my_linkedin_cookies.json"
        results = scrape_linkedin_people_search(names, LINKEDIN_EMAIL, LINKEDIN_PASSWORD, cookies_file)

        # Construct final result format
        formatted_results = {}

        for name, url in results.items():
            name_parts = name.strip().split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Save profile to DB
            new_profile = Profile(first_name=first_name, last_name=last_name, url=url)
            db.session.add(new_profile)

            # Update matching People record
            people_match = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()
            if people_match:
                people_match.linkedin = url
            else:
                print(f"No matching People record found for {first_name} {last_name}")

            # Add to formatted result
            full_name_key = f"{first_name} {last_name}".strip()
            formatted_results[full_name_key] = url

        # Commit DB changes
        db.session.commit()

        return jsonify({
            "message": "Scraping successful",
            "results": formatted_results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500