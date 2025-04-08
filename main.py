from apify_client import ApifyClient
import json, time
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from typing import Optional
from pydantic import BaseModel
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Validate required environment variables
required_env_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "APIFY_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = FastAPI()

# Initialize Supabase client
try:
    supabase: Client = create_client(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    logger.info("Successfully connected to Supabase")
except Exception as e:
    logger.error(f"Failed to connect to Supabase: {str(e)}")
    raise

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
client = ApifyClient(APIFY_API_KEY)

class JobSearchRequest(BaseModel):
    jobTitle: str
    region: Optional[str] = "Unknown"
    country: str

def search_linkedin(preprocessed_title: str, job_region: str, job_country: str) -> list:
    job_title = preprocessed_title
    jobs_list = []
    try:
        location = job_country if job_region == "Unknown" else job_region
        logger.info(f"Searching LinkedIn for: {job_title} in {location}")

        run_input = {
            "location": location,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": "US"
            },
            "publishedAt": "r86400",
            "rows": 50,
            "title": job_title
        }
        time.sleep(10)
        run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        logger.info(f"Found {len(dataset_items)} jobs from LinkedIn")
        
        jobs_list = dataset_items
    except Exception as e:
        logger.error(f"Error searching LinkedIn: {str(e)}")
        error_message = f"Error searching LinkedIn: {str(e)}"
        return [{"Error_message": error_message}]
    
    return jobs_list

@app.post('/api/search')
async def main(data: JobSearchRequest):
    try:
        if not data.jobTitle or not data.country:
            raise HTTPException(status_code=400, detail="Job title and job country are required")
        
        jobs_list = []
        
        if "," in data.jobTitle:
            updated_job_title = data.jobTitle.split(",")
            for title in updated_job_title:
                preprocessed_title = title.strip()
                linkedin_jobs = search_linkedin(preprocessed_title, data.region, data.country)
                jobs_list.extend(linkedin_jobs)
                time.sleep(10)
        else:
            linkedin_jobs = search_linkedin(data.jobTitle, data.region, data.country)
            jobs_list.extend(linkedin_jobs)

        # Save to local JSON file with proper error handling
        try:
            with open('jobs_list.json', 'w') as f:
                json.dump(jobs_list, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving jobs to file: {str(e)}")
        
        # Store in Supabase with transaction handling
        try:
            for job in jobs_list:
                if job.get("companyName") is None:
                    continue
                job_data = {
                    "company": job.get("companyName"),
                    "company_url": job.get("companyUrl"),
                    "salary": job.get("salary"), 
                    "linkedin_url": job.get("jobUrl"), 
                    "indeed_url": job.get("applyUrl"), 
                    "apply_url": job.get("applyUrl"), 
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
                
                try:
                    result = supabase.table("scraped_jobs").insert(job_data).execute()
                    logger.info(f"Successfully inserted job: {job_data['title']}")
                except Exception as e:
                    logger.error(f"Failed to insert job {job_data['title']}: {str(e)}")
                    continue  # Continue with next job even if one fails
        except Exception as e:
            logger.error(f"Error storing jobs in Supabase: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error storing jobs in database: {str(e)}")
        
            # Continue execution as this is not critical
      
        return jobs_list
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/test')
async def test(data: dict):
    try:
        logger.info(f"Received test data: {data}")
        return {"message": "Data was received successfully"}
    except Exception as e:
        logger.error(f"Error in test function: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8080)