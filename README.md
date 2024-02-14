# File Converter and Web Scraper
This application is a Streamlit-based web app that provides file conversion and web scraping functionalities.

## Features
File Conversion: The application can convert DOCX and XML files to JSON format. The converted JSON data is displayed on the web page and can also be downloaded.

Web Scraping: The application can scrape web content from a list of URLs provided in a JSON file. The scraped data includes the URL, title, publish date, and content of each web page. The scraped data is displayed on the web page and can also be downloaded in JSON format.

## How It Works
File Conversion
The application uses the python-docx and xmltodict libraries to convert DOCX and XML files to JSON, respectively.

For DOCX files, the application reads the file using python-docx, extracts the text and style of each paragraph, and stores them in a list of dictionaries. The list is then converted to JSON format.

For XML files, the application reads the file and uses xmltodict to convert the XML data to a Python dictionary. The dictionary is then converted to JSON format.

## Web Scraping
The application uses the requests and beautifulsoup4 libraries to scrape web content.

The application reads a JSON file containing a list of URLs. For each URL, the application sends a GET request to retrieve the web page content. The content is parsed using beautifulsoup4 to extract the title, publish date, and text content. The extracted data is stored in a dictionary and added to a list. The list is then converted to JSON format.

## How to Use
Run the Streamlit app.
Use the file uploaders to upload a DOCX or XML file for conversion to JSON. The converted JSON data will be displayed on the web page and can be downloaded by clicking the "Download JSON File" link.
Use the file uploader to upload a JSON file containing a list of URLs for web scraping. The scraped data will be displayed on the web page and can be downloaded by clicking the "Download Scraped Data JSON File" link.

## Dependencies
streamlit
python-docx
xmltodict
requests
beautifulsoup4
re
json
base64

## run
'pip install streamlit python-docx xmltodict requests beautifulsoup4'
'streamlit run app.py'

