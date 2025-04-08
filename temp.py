def search_indeed(title, location):
    jobs_list = []
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
            jobs_list.append(individual)
    except Exception as e:
        print(f"Error searching Indeed: {str(e)}")
    
    return jobs_list

def search_glassdoor(title, location, country):
    jobs_list = []
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
            jobs_list.append(individual)
    except Exception as e:
        print(f"Error searching Glassdoor: {str(e)}")
    
    return jobs_list

def search_ziprecruiter(title, location, country):
    jobs_list = []
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
            jobs_list.append(individual)
    except Exception as e:
        print(f"Error searching Ziprecruiter: {str(e)}")
    
    return jobs_list