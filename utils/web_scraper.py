import requests
from bs4 import BeautifulSoup

def scrape_web_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.get_text() if title_tag else 'No Title Found'
        paragraphs = soup.find_all('p')
        text_content = ' '.join(p.get_text() for p in paragraphs)
        paragraphs = [paragraph.strip() for paragraph in text_content.split('\n') if paragraph.strip()]
        return {"url": url, "title": title, "content": paragraphs}
    else:
        return {"error": f"Failed to scrape the web content: HTTP Status Code {response.status_code}"}