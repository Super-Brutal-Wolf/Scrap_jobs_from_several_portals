from apify_client import ApifyClient
import pandas as pd
import openpyxl
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)

APIFY_API_KEY = "apify_api_sWo8upg6Me4zM2FY6ui1H4KMr21f0V4nzs3U"

client = ApifyClient(APIFY_API_KEY)

def search_linkedin(title, location):
    job_list = []
    try:
        print("Searching for LinkedIn")
        run_input = {
            "title": title,
            "location": location,
            "publishedAt": "r86400",
            "rows": 250,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": "US"
            },
        }
        
        run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(dataset_items)} jobs from LinkedIn")
        
        for item in dataset_items:
            individual = {
                "title": item.get('title'),
                "description": item.get('description'),
                "companyName": item.get('companyName'),
                "companyUrl": item.get('companyUrl'),
                "jobUrl": item.get('jobUrl'),
                "location": item.get('location'),
                "contractType": item.get('contractType'),
                "publisher": "LinkedIn",
                "publishedAt": item.get('publishedAt'),
                "postedTime": item.get('postedTime'),
                "experienceLevel": item.get('experienceLevel'),
                "applyUrl": item.get('applyUrl'),
            }
            job_list.append(individual)
    except Exception as e:
        print(f"Error searching LinkedIn: {str(e)}")
    
    return job_list

def search_indeed(title, location):
    job_list = []
    try:
        print("Searching for Indeed")
        searching_title = title.strip().replace(" ", "+")
        searching_location = location.strip().replace(" ", "+")
        searching_url = f"https://www.indeed.com/jobs?q={searching_title}&l={searching_location}&fromage=1"
        
        run_input = {
            "count": 500,
            "findContacts": False,
            "outputSchema": "raw",
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": "US"
            },
            "scrapeJobs.scrapeCompany": False,
            "scrapeJobs.searchUrl": searching_url,
            "useBrowser": True
        }
        
        run = client.actor("qA8rz8tR61HdkfTBL").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(dataset_items)} jobs from Indeed")
        
        for item in dataset_items:
            individual = {
                "title": item.get('title'),
                "description": item.get('jobDescription'),
                "companyName": item.get('company'),
                "companyUrl": item.get('companyOverviewLink'),
                "location": item.get('jobLocationCity'),
                "publisher": "Indeed",
                "postedTime": item.get('formattedRelativeTime'),
                "applyUrl": item.get('thirdPartyApplyUrl'),
            }
            job_list.append(individual)
    except Exception as e:
        print(f"Error searching Indeed: {str(e)}")
    
    return job_list

def search_glassdoor(title, location, country):
    job_list = []
    try:
        print("Searching for Glassdoor")
        run_input = {
            "country": country,
            "city": location,
            "engines": "2",
            "last": "1d",
            "distance": "50",
            "delay": 2,
            "max": 500,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": "US"
            },
            "title": title
        }
        
        run = client.actor("PskQAJMqsgeJHXSDz").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(dataset_items)} jobs from Glassdoor")
        
        for item in dataset_items:
            individual = {
                "title": item.get('title'),
                "description": item.get('description'),
                "companyName": item.get('company'),
                "companyUrl": item.get('company_url'),
                "jobUrl": item.get('job_url'),
                "location": item.get('location'),
                "publisher": "Glassdoor",
            }
            job_list.append(individual)
    except Exception as e:
        print(f"Error searching Glassdoor: {str(e)}")
    
    return job_list

def search_ziprecruiter(title, location, country):
    job_list = []
    try:
        print("Searching for Ziprecruiter")
        run_input = {
            "country": country,
            "city": location,
            "engines": "1",  
            "last": "1d",
            "distance": "50",
            "delay": 1,
            "max": 500,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": "US"
            },
            "title": title
        }
        
        run = client.actor("PskQAJMqsgeJHXSDz").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(dataset_items)} jobs from Ziprecruiter")
        
        for item in dataset_items:
            individual = {
                "title": item.get('title'),
                "description": item.get('description'),
                "companyName": item.get('company'),
                "companyUrl": item.get('company_url'),
                "jobUrl": item.get('job_url'),
                "location": item.get('location'),
                "publisher": "Ziprecruiter",
            }
            job_list.append(individual)
    except Exception as e:
        print(f"Error searching Ziprecruiter: {str(e)}")
    
    return job_list

@app.route('/api/search', methods=['POST'])
def main():
    try:
        data = request.get_json()
        title = data.get('jobTitle', '')
        location = data.get('region', '')
        country = data.get('country', '')
        
        if not title or not location:
            return jsonify({"error": "Job title and location are required"}), 400
        
        job_list = []
        
        # Search LinkedIn
        linkedin_jobs = search_linkedin(title, location)
        job_list.extend(linkedin_jobs)
        
        # Wait between API calls to avoid rate limiting
        time.sleep(3)
        
        # Search Indeed
        indeed_jobs = search_indeed(title, location)
        job_list.extend(indeed_jobs)
        
        # Wait between API calls
        time.sleep(3)
        
        # Search Glassdoor
        glassdoor_jobs = search_glassdoor(title, location, country)
        job_list.extend(glassdoor_jobs)
        
        # Wait between API calls
        time.sleep(3)
    
        # Search Ziprecruiter
        ziprecruiter_jobs = search_ziprecruiter(title, location, country)
        job_list.extend(ziprecruiter_jobs)
        
        return jsonify(job_list)
    
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test():
    print("Data was Received successfully")
    return jsonify({'message': 'Data was received successfully'})

if __name__ == '__main__':
    print("Server started")
    serve(app, host="127.0.0.1", port=5001)
