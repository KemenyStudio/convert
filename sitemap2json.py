import re
import json
import base64
import requests
from bs4 import BeautifulSoup
import xmltodict
import streamlit as st

st.title("Web Scraper App")

# Utility functions
def clean_text(text):
    """Remove excessive whitespace and clean text."""
    return re.sub(r'\s+', ' ', text).strip()

# Web scraping function
def scrape_content(urls):
    scraped_data = []
    for url in urls:
        page_data = {"url": url, "title": None, "publish_date": None, "content": None}
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            page_data["title"] = title_tag.get_text() if title_tag else 'No Title Found'
            date_tag = soup.find(lambda tag: tag.name == "meta" and "publish" in tag.get("name", "").lower())
            page_data["publish_date"] = date_tag["content"] if date_tag else None
            raw_content = soup.get_text()
            page_data["content"] = clean_text(raw_content)
        except requests.RequestException as e:
            page_data["content"] = f"Failed to retrieve content: {e}"
        scraped_data.append(page_data)
    return scraped_data

# Sitemap handler
sitemap_url = st.text_input("Enter the sitemap.xml URL")
if sitemap_url:
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        xml_content = response.content
        data_dict = xmltodict.parse(xml_content)
        if 'urlset' in data_dict and 'url' in data_dict['urlset']:
            urls = [url_entry['loc'] for url_entry in data_dict['urlset']['url']]
            progress_bar = st.progress(0)
            scraped_data = []
            total_urls = len(urls)
            for i, url in enumerate(urls, start=1):
                progress_bar.progress(i / total_urls)
                page_data = scrape_content([url])
                scraped_data.extend(page_data)
            st.json(scraped_data)
            scraped_data_json = json.dumps(scraped_data, ensure_ascii=False, indent=4)
            b64 = base64.b64encode(scraped_data_json.encode('utf-8')).decode()
            download_href = f'<a href="data:file/json;base64,{b64}" download="scraped_data.json">Download Scraped Data JSON File</a>'
            st.markdown(download_href, unsafe_allow_html=True)
            progress_bar.empty()
    except requests.RequestException as e:
        st.write(f"Failed to retrieve sitemap: {e}")