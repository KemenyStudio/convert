import requests
import xmltodict
from .web_scraper import scrape_web_content

def handle_sitemap_url(sitemap_url):
    response = requests.get(sitemap_url)
    response.raise_for_status()
    sitemap = xmltodict.parse(response.content)
    scraped_data = []

    if 'urlset' in sitemap:
        urls = [url_entry['loc'] for url_entry in sitemap['urlset']['url']]
        for url in urls:
            page_data = scrape_web_content(url)
            scraped_data.append(page_data)
    elif 'sitemapindex' in sitemap:
        sitemaps = [sitemap_entry['loc'] for sitemap_entry in sitemap['sitemapindex']['sitemap']]
        for sitemap_url in sitemaps:
            scraped_data.extend(handle_sitemap_url(sitemap_url))

    return scraped_data