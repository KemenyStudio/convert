import re
import json
import base64
import requests
import sys
from bs4 import BeautifulSoup
from docx import Document
import xmltodict
import streamlit as st

st.title("File Converter App")

# Utility functions
def clean_text(text):
    """Remove excessive whitespace and clean text."""
    return re.sub(r'\s+', ' ', text).strip()

# File conversion functions
def docx_to_json(docx_file):
    doc = Document(docx_file)
    data = [{"text": para.text, "style": para.style.name} for para in doc.paragraphs]
    return json.dumps(data, indent=4)

def xml_to_json(xml_file):
    xml_content = xml_file.read()
    data_dict = xmltodict.parse(xml_content)
    return json.dumps(data_dict, indent=4)

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

# File upload handlers
def handle_file_upload(file_type, process_function):
    uploaded_file = st.file_uploader(f"{file_type} to JSON", type=[file_type])
    if uploaded_file is not None:
        json_data = process_function(uploaded_file)
        st.json(json_data)
        b64 = base64.b64encode(json_data.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="converted.json">Download JSON File</a>'
        st.markdown(href, unsafe_allow_html=True)

handle_file_upload("docx", docx_to_json)
handle_file_upload("xml", xml_to_json)


# Json to Web scraping handler
uploaded_json_file = st.file_uploader("JSON file with URLs Web Scraper", type=["json"])
if uploaded_json_file is not None:
    json_content = json.load(uploaded_json_file)
    if 'urlset' in json_content and 'url' in json_content['urlset']:
        urls = [url_entry['loc'] for url_entry in json_content['urlset']['url']]
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

# Sitemap Web Scrape function to your code
def handle_sitemap_url(sitemap_url, progress_bar=None, counter=None, file_index=0, scraped_data=None):
    if scraped_data is None:
        scraped_data = []
    response = requests.get(sitemap_url)
    response.raise_for_status()
    sitemap = xmltodict.parse(response.content)
    progress_bar_value = 0  # Initialize progress bar value
    if 'urlset' in sitemap:
        total_urls = len(sitemap['urlset']['url'])
        for i, url_entry in enumerate(sitemap['urlset']['url']):
            url = url_entry['loc']
            if url.endswith('.xml'):
                # This is a nested sitemap, handle it recursively
                if progress_bar is not None:
                    progress_bar_value = i / total_urls
                    progress_bar.progress(min(progress_bar_value + 0.01, 1.0))
                scraped_data, file_index = handle_sitemap_url(url, progress_bar, counter, file_index, scraped_data)
            else:
                # This is a regular page, scrape its content
                page_data = scrape_content([url])
                scraped_data.extend(page_data)
                counter[0] += 1
                st.write(f"Scraped {counter[0]} URLs so far.")
                # Check if the size of scraped_data exceeds 6MB
                if sys.getsizeof(scraped_data) > 6 * 1024 * 1024:
                    # Write the current scraped_data to a file
                    with open(f'scraped_data_{file_index}.json', 'w') as f:
                        json.dump(scraped_data, f)
                    # Reset scraped_data and increment file_index
                    scraped_data = []
                    file_index += 1
    elif 'sitemapindex' in sitemap:
        total_sitemaps = len(sitemap['sitemapindex']['sitemap'])
        for i, sitemap_entry in enumerate(sitemap['sitemapindex']['sitemap']):
            url = sitemap_entry['loc']
            # This is a nested sitemap, handle it recursively
            if progress_bar is not None:
                progress_bar_value = i / total_sitemaps
                progress_bar.progress(min(progress_bar_value + 0.01, 1.0))
            scraped_data, file_index = handle_sitemap_url(url, progress_bar, counter, file_index, scraped_data)
    return scraped_data, file_index

# Add this to your Streamlit interface
sitemap_url = st.text_input("Sitemap URL")
if sitemap_url:
    progress_bar = st.progress(0)
    counter = [0]  # Use a list to hold the counter value
    scraped_data, file_index = handle_sitemap_url(sitemap_url, progress_bar, counter)
    # Write the remaining scraped_data to a file
    with open(f'scraped_data_{file_index}.json', 'w') as f:
        json.dump(scraped_data, f)
    st.json(scraped_data)