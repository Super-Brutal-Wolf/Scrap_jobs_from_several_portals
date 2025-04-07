from apify_client import ApifyClient
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json

# app = Flask(__name__)
# CORS(app)

APIFY_API_KEY = "apify_api_sWo8upg6Me4zM2FY6ui1H4KMr21f0V4nzs3U"

client = ApifyClient(APIFY_API_KEY)

def search_linkedin(job_title, job_region, job_country):
    jobs_list = []
    try:
        print("Searching for LinkedIn")
        if job_region == "Unknown":
            location = job_country
        else:
            location = job_region 

        run_input = {
            "location": location,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": [
                    "RESIDENTIAL"
                ],
                "apifyProxyCountry": "US"
            },
            "publishedAt": "r86400",
            "rows": 1000, # maximum is 1000
            "title": job_title
        }
        
        run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(dataset_items)} jobs from LinkedIn")
        
        jobs_list = dataset_items
    except Exception as e:
        print(f"Error searching LinkedIn: {str(e)}")
    
    return jobs_list

# def search_indeed(title, location):
#     jobs_list = []
#     try:
#         print("Searching for Indeed")
#         searching_title = title.strip().replace(" ", "+")
#         searching_location = location.strip().replace(" ", "+")
#         searching_url = f"https://www.indeed.com/jobs?q={searching_title}&l={searching_location}&fromage=1"
        
#         run_input = {
#             "count": 500,
#             "findContacts": False,
#             "outputSchema": "raw",
#             "proxy": {
#                 "useApifyProxy": True,
#                 "apifyProxyGroups": ["RESIDENTIAL"],
#                 "apifyProxyCountry": "US"
#             },
#             "scrapeJobs.scrapeCompany": False,
#             "scrapeJobs.searchUrl": searching_url,
#             "useBrowser": True
#         }
        
#         run = client.actor("qA8rz8tR61HdkfTBL").call(run_input=run_input)
#         dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
#         print(f"Found {len(dataset_items)} jobs from Indeed")
        
#         for item in dataset_items:
#             individual = {
#                 "title": item.get('title'),
#                 "description": item.get('jobDescription'),
#                 "companyName": item.get('company'),
#                 "companyUrl": item.get('companyOverviewLink'),
#                 "location": item.get('jobLocationCity'),
#                 "publisher": "Indeed",
#                 "postedTime": item.get('formattedRelativeTime'),
#                 "applyUrl": item.get('thirdPartyApplyUrl'),
#             }
#             jobs_list.append(individual)
#     except Exception as e:
#         print(f"Error searching Indeed: {str(e)}")
    
#     return jobs_list

# def search_glassdoor(title, location, country):
#     jobs_list = []
#     try:
#         print("Searching for Glassdoor")
#         run_input = {
#             "country": country,
#             "city": location,
#             "engines": "2",
#             "last": "1d",
#             "distance": "50",
#             "delay": 2,
#             "max": 500,
#             "proxy": {
#                 "useApifyProxy": True,
#                 "apifyProxyGroups": ["RESIDENTIAL"],
#                 "apifyProxyCountry": "US"
#             },
#             "title": title
#         }
        
#         run = client.actor("PskQAJMqsgeJHXSDz").call(run_input=run_input)
#         dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
#         print(f"Found {len(dataset_items)} jobs from Glassdoor")
        
#         for item in dataset_items:
#             individual = {
#                 "title": item.get('title'),
#                 "description": item.get('description'),
#                 "companyName": item.get('company'),
#                 "companyUrl": item.get('company_url'),
#                 "jobUrl": item.get('job_url'),
#                 "location": item.get('location'),
#                 "publisher": "Glassdoor",
#             }
#             jobs_list.append(individual)
#     except Exception as e:
#         print(f"Error searching Glassdoor: {str(e)}")
    
#     return jobs_list

# def search_ziprecruiter(title, location, country):
#     jobs_list = []
#     try:
#         print("Searching for Ziprecruiter")
#         run_input = {
#             "country": country,
#             "city": location,
#             "engines": "1",  
#             "last": "1d",
#             "distance": "50",
#             "delay": 1,
#             "max": 500,
#             "proxy": {
#                 "useApifyProxy": True,
#                 "apifyProxyGroups": ["RESIDENTIAL"],
#                 "apifyProxyCountry": "US"
#             },
#             "title": title
#         }
        
#         run = client.actor("PskQAJMqsgeJHXSDz").call(run_input=run_input)
#         dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
#         print(f"Found {len(dataset_items)} jobs from Ziprecruiter")
        
#         for item in dataset_items:
#             individual = {
#                 "title": item.get('title'),
#                 "description": item.get('description'),
#                 "companyName": item.get('company'),
#                 "companyUrl": item.get('company_url'),
#                 "jobUrl": item.get('job_url'),
#                 "location": item.get('location'),
#                 "publisher": "Ziprecruiter",
#             }
#             jobs_list.append(individual)
#     except Exception as e:
#         print(f"Error searching Ziprecruiter: {str(e)}")
    
#     return jobs_list

# @app.route('/api/search', methods=['POST'])
def main(job_title, job_region, job_country):
    # try:
    # data = request.get_json()
    # job_title = data.get('jobTitle', '')
    # job_region = data.get('region', '')
    # job_country = data.get('country', '')
    
    # if not job_title or not job_country:
    #     return jsonify({"error": "Job title and job country are required"}), 400
    
    jobs_list = []
    
    # Search LinkedIn
    linkedin_jobs = search_linkedin(job_title, ob_region, job_country)
    jobs_list.extend(linkedin_jobs)

    time.sleep(3)
    
    with open('jobs_list.json', 'w') as f:
        json.dump(jobs_list, f, indent=4)
      
    # return jsonify(jobs_list)
    
    # except Exception as e:
    #     print(f"Error in main function: {str(e)}")
    #     return jsonify({"error": str(e)}), 500

# @app.route('/api/test', methods=['POST'])
# def test():
#     print("Data was Received successfully")
#     return jsonify({'message': 'Data was received successfully'})

if __name__ == '__main__':
    # print("Server started")
    # serve(app, host="127.0.0.1", port=5001)

    job_title = input("Enter your desired job title(example: 'receptionist'): ")
    job_region = input("Enter your desired job region(example: 'New York or Unknown'): ")
    job_country = input("Enter your desired job country(example: 'United States'): ")
    main(job_title, job_region, job_country)