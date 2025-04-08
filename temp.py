

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

