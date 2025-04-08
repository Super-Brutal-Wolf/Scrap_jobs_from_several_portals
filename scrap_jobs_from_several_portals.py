from apify_client import ApifyClient
import json, time
from fastapi import FastAPI, HTTPException
import uvicorn
from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Initialize Supabase client
supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

client = ApifyClient(APIFY_API_KEY)

def search_linkedin(preprocessed_title, job_region, job_country):
    job_title = preprocessed_title
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
            "rows": 50, # maximum is 1000
            "title": job_title
        }
        
        run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(dataset_items)} jobs from LinkedIn")
        
        jobs_list = dataset_items
    except Exception as e:
        print(f"Error searching LinkedIn: {str(e)}")
        error_message = f"Error searching LinkedIn: {str(e)}"
        return [{"Error_message": error_message}]
    
    return jobs_list



@app.post('/api/search')
async def main(data: dict):
    try:
        job_title = data.get('jobTitle', '')
        job_region = data.get('region', '')
        job_country = data.get('country', '')
        
        if not job_title or not job_country:
            return {"error": "Job title and job country are required"}, 400
        
        jobs_list = []
        
        if "," in job_title:
            updated_job_title = job_title.split(",")

            for title in updated_job_title:
                preprocessed_title = title.strip()

                linkedin_jobs = search_linkedin(preprocessed_title, job_region, job_country)
                jobs_list.extend(linkedin_jobs)

        else:
            preprocessed_title = job_title
            
            linkedin_jobs = search_linkedin(preprocessed_title, job_region, job_country)
            jobs_list.extend(linkedin_jobs)
        
        # Store in Supabase
        for job in jobs_list:
            if job.get("companyName") is None:
                continue
            job_data = {
                "company": job.get("companyName"),
                "company_url": job.get("companyUrl"),
                "salary": job.get("salary"), 
                "linkedin_url": job.get("jobUrl"), 
                "indeed_url": job.get("applyUrl"), 
                "apply_url":job.get("applyUrl"), 
                "job_url": job.get("jobUrl"), 
                "contract_type": job.get("contractType"), 
                "job_description": job.get("description"), 
                "experience_level": job.get("experienceLevel"), 
                "location": job.get("location"), 
                "posted_time": job.get("postedTime"), 
                "published_at": job.get("publishedAt"), 
                "publisher": job.get("publisher", "Linkedin"), 
                "title": job.get("title"), 
                "created_at": datetime.now().isoformat(), 
                "other": job.get("benefits") 
            }
            
            supabase.table("jobs").insert(job_data).execute()
        
        # Also save to local JSON file
        with open('jobs_list.json', 'w') as f:
            json.dump(jobs_list, f, indent=4)
      
        return jobs_list
    
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        return ({"error": str(e)}), 500

@app.post('/api/test')
async def test(data: dict):
    try:
        print(data)
        print("Data was Received successfully")
        return {"message": "Data was received successfully"}
    except Exception as e:
        print(f"Error in test function: {str(e)}")
        return ({"error": str(e)}), 500


if __name__ == '__main__':
    # job_title = input("Enter your desired job title(example: 'receptionist, web developer...'): ")
    # job_region = input("Enter your desired job region(example: 'New York or Unknown'): ")
    # job_country = input("Enter your desired job country(example: 'United States'): ")

    uvicorn.run(app, host="127.0.0.1", port=8080)