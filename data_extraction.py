import pandas as pd
from bs4 import BeautifulSoup
import requests
import os

# Load input data
input_df = pd.read_excel("Input.xlsx")

# Ensure output directory
os.makedirs("extracted_articles", exist_ok=True)

# Scrape and save articles
for index, row in input_df.iterrows():
    url_id, url = row['URL_ID'], row['URL']
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title and article
        title = soup.find('h1').get_text()
        paragraphs = soup.find_all('p')
        article_text = "\n".join([p.get_text() for p in paragraphs])

        # Save to text file
        with open(f"extracted_articles/{url_id}.txt", "w", encoding="utf-8") as file:
            file.write(f"{title}\n{article_text}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
