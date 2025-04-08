from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
import sys
from jobs_list import jobs_list

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
load_dotenv()

required_env_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

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

def main():
    try:
        for job in jobs_list:
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
                result = supabase.table('scraped_jobs').insert(job_data).execute()
                logger.info(f"Successfully inserted job: {job_data['title']}")
            except Exception as e:
                logger.error(f"Failed to insert job {job_data['title']}: {str(e)}")
                continue  # Continue with next job even if one fails
    except Exception as e:
        logger.error(f"Critical error in main function: {str(e)}")
        raise  # Re-raise the exception to stop execution

def calculator_length():
    print(len(jobs_list))

if __name__ == "__main__":
    calculator_length()
