import requests
import os
from bs4 import BeautifulSoup

from lib.parsers import scrape_table

URL = 'https://my.nycha.info/Outages/Outages.aspx'
page = requests.get(URL)
content = page.content
soup = BeautifulSoup(content, 'html.parser')

if not os.path.exists('data'):
    os.mkdir('data')

scrape_table(soup, 'heatHotWater', 'Planned')
scrape_table(soup, 'heatHotWater', 'ClosedIn24Hours')
scrape_table(soup, 'heatHotWater', 'Open')

scrape_table(soup, 'elevator', 'Planned')
scrape_table(soup, 'elevator', 'ClosedIn24Hours')
scrape_table(soup, 'elevator', 'Open')

scrape_table(soup, 'electric', 'Planned')
scrape_table(soup, 'electric', 'ClosedIn24Hours')
scrape_table(soup, 'electric', 'Open')

scrape_table(soup, 'gas')
