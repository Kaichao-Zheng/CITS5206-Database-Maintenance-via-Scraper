import time
from helper.ip_scraping import scrape_https_proxies 
from app import db
from app.models import IP
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify,send_file
from sqlalchemy.exc import SQLAlchemyError
from app.main.scraping import sc
from flask_login import current_user, login_user,logout_user,login_required

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
    


    