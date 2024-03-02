import requests
from bs4 import BeautifulSoup
import streamlit as st
import json

def scrape_web_content(url):
    """Scrape the title and text content from a given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            title = title_tag.get_text() if title_tag else 'No Title Found'
            paragraphs = soup.find_all('p')
            if paragraphs:
                text_content = ' '.join(p.get_text() for p in paragraphs)
                # Split the text content into paragraphs
                paragraphs = [paragraph.strip() for paragraph in text_content.split('\n') if paragraph.strip()]
            else:
                paragraphs = ['No text content found']
            return {"url": url, "title": title, "content": paragraphs}
        else:
            return {"error": f"Failed to scrape the web content: HTTP Status Code {response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to scrape the web content: {e}"}

# Streamlit interface
st.title('Web Scraper')
url = st.text_input('Enter the URL you want to scrape')

if st.button('Start scraping'):
    if url:
        result = scrape_web_content(url)
        st.write(result)
        # Save result to a file
        with open('result.json', 'w') as f:
            json.dump(result, f)
    else:
        st.write('Please enter a URL.')
