import requests
from bs4 import BeautifulSoup
import pandas as pd
import aiohttp
import asyncio
from aiohttp import ClientSession
import urllib3
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def fetch_metadata(session, url):
    try:
        async with session.get(url, timeout=10, ssl=False) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'lxml')

           
            title = soup.title.string.strip() if soup.title else None
            
            
            description_tag = soup.find("meta", attrs={"name": "description"})
            description = description_tag['content'].strip() if description_tag else None

            
            eligibility = "Eligible" if title and description else "Ineligible"

            return {
                "url": url,
                "title": title if title else "No Title",
                "description": description if description else "No Description",
                "eligibility": eligibility
            }
    except Exception as e:
        return {
            "url": url,
            "title": "Error",
            "description": str(e),
            "eligibility": "Ineligible"
        }

async def process_websites_async(urls):
    results = []
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch_metadata(session, url))
        results = await asyncio.gather(*tasks)
    return results

def bulk_website_checker(input_file, output_file):
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    start_time = time.time()

   
    urls = df['URL'].tolist()
    results = asyncio.run(process_websites_async(urls))

   
    results_df = pd.DataFrame(results)

    try:
        results_df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving the results: {e}")

    end_time = time.time()
    print(f"Processing completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    input_file = 'websites.csv'   
    output_file = 'results.csv'    
    bulk_website_checker(input_file, output_file)