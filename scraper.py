import requests
import os
from bs4 import BeautifulSoup

from lib.parsers import scrape_outages

URL = 'https://my.nycha.info/Outages/Outages.aspx'
page = requests.get(URL)
content = page.content
soup = BeautifulSoup(content, 'html.parser')

scrape_outages(soup, 'heatHotWater', 'Planned')
scrape_outages(soup, 'heatHotWater', 'ClosedIn24Hours')
scrape_outages(soup, 'heatHotWater', 'Open')

scrape_outages(soup, 'elevator', 'Planned')
scrape_outages(soup, 'elevator', 'ClosedIn24Hours')
scrape_outages(soup, 'elevator', 'Open')

scrape_outages(soup, 'electric', 'Planned')
scrape_outages(soup, 'electric', 'ClosedIn24Hours')
scrape_outages(soup, 'electric', 'Open')

scrape_outages(soup, 'gas')
