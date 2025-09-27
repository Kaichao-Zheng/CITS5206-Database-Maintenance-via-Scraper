import time
from .helper.ip_scraping import scrape_https_proxies 
from .helper.profile_url_scrape import scrape_linkedin_people_search
from app import db
from app.models import IP, People
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify,send_file
from sqlalchemy.exc import SQLAlchemyError
from app.main.scrape import sc
from flask_login import login_required
import os
import sqlalchemy as sa
from .helper.scrape_information import scrape_profiles
import io
import csv
from dotenv import load_dotenv

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

# Get People without organization/role/city 
# Not part of the scope of this project
def conditional_get_people_names_for_information_searching(number: int):
    session = db.session

    people_records = session.query(People).order_by(People.id)  

    result = []
    for person in people_records:
       
        if person.organization and person.role and person.city:
            print(f"{person.first_name} {person.last_name} has already enough information")
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
            people_match = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()
            if people_match:
                people_match.linkedin = url
                formatted_results[f"{first_name} {last_name}".strip()] = url
            else:
                print(f"No matching People record found for {first_name} {last_name}")

        # Commit DB changes
        db.session.commit()

        return jsonify({
            "message": "Scraping successful",
            "results": formatted_results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@sc.route('/scrape_information', methods=['GET'])
def scrape_linkedin_information():
    try:
        number = request.args.get('number', default=10, type=int)
        
        # Step 1: Get names
        names = conditional_get_people_names_for_information_searching(number)
        if not names:
            return jsonify({"error": "No names found to scrape"}), 400

        # Step 2: Get People without organization/role/city but with linkedin URL
        people_records = db.session.query(People).filter(
            People.linkedin.isnot(None),
            People.linkedin != ""  # skip empty
        ).limit(number).all()

        if not people_records:
            return jsonify({"error": "No People with LinkedIn URLs found"}), 404
        
        profile_map = {
            f"{p.first_name} {p.last_name}".strip(): p.linkedin
            for p in people_records
        }

        # Step 3: Scrape profiles
        scraped_results = scrape_profiles(profile_map, LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

        # Step 4: Update People table with scraped data
        for name, info in scraped_results.items():
            name_parts = name.strip().split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            person = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()

            if person:
                person.organization = info.get("company", "")
                person.role = info.get("position", "")
                person.city = info.get("location", "")
            else:
                print(f"⚠️ No matching People record to update for {name}")

        db.session.commit()

        # Step 5: Return scraped results
        return jsonify({
            "message": "Scraping successful",
            "results": scraped_results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# no filter of names
@sc.route('/scrape_from_linkedin', methods=['GET'])
@login_required
def scrape_from_linkedin():
    try:
        number = request.args.get('number', default=10, type=int)

        # Step 1: Get People records (limit by number)
        people_records = db.session.query(People).limit(number).all()
        if not people_records:
            return jsonify({"error": "No People records found"}), 404

        # Step 2: Build list of names (only if linkedin is missing)
        names = [
            f"{p.first_name} {p.last_name}".strip()
            for p in people_records
            if not p.linkedin  # skip if already has a LinkedIn URL
        ]

        # Step 3: Scrape LinkedIn URLs
        cookies_file = "my_linkedin_cookies.json"
        scraped_urls = scrape_linkedin_people_search(
            names, LINKEDIN_EMAIL, LINKEDIN_PASSWORD, cookies_file
        )

        # Step 4: Update People table with LinkedIn URLs
        for name, url in scraped_urls.items():
            fn, *ln = name.strip().split()
            first_name, last_name = fn, " ".join(ln)
            person = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()
            if person:
                person.linkedin = url

        # Step 5: Scrape detailed profile info
        profile_map = {
            f"{p.first_name} {p.last_name}".strip(): p.linkedin
            for p in people_records if p.linkedin
        }
        scraped_info = scrape_profiles(profile_map, LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

        # Step 6: Update People table with scraped info
        for name, info in scraped_info.items():
            fn, *ln = name.strip().split()
            first_name, last_name = fn, " ".join(ln)
            person = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()
            if person:
                person.organization = info.get("company", "")
                person.role = info.get("position", "")
                person.city = info.get("location", "")

        db.session.commit()


        # Step 4: Fetch all People (or limit to updated ones if you prefer)
        all_people = db.session.query(People).all()

        # Step 5: Write CSV to memory (no temp file needed)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([col.name for col in People.__table__.columns])  # header row
        for p in all_people:
            writer.writerow([getattr(p, col.name) for col in People.__table__.columns])

        csv_data = output.getvalue()
        output.close()

        with open("./tmp/updated.csv", "w", newline='', encoding='utf-8') as f:
            f.write(csv_data)

        # Step 8: Return entire People table as JSON
        all_people = db.session.query(People).all()
        result = [
            {col.name: getattr(p, col.name) for col in People.__table__.columns}
            for p in all_people
        ]

        return jsonify({"message": "Scraping successful", "people": result}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
       