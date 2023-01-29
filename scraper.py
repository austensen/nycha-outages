import requests
import os
from bs4 import BeautifulSoup

from lib.daily_scrape import scrape_daily_outages

URL = 'https://my.nycha.info/Outages/Outages.aspx'
page = requests.get(URL)
content = page.content
soup = BeautifulSoup(content, 'html.parser')

scrape_daily_outages(soup, 'heatHotWater', 'Planned')
scrape_daily_outages(soup, 'heatHotWater', 'ClosedIn24Hours')
scrape_daily_outages(soup, 'heatHotWater', 'Open')

scrape_daily_outages(soup, 'elevator', 'Planned')
scrape_daily_outages(soup, 'elevator', 'ClosedIn24Hours')
scrape_daily_outages(soup, 'elevator', 'Open')

scrape_daily_outages(soup, 'electric', 'Planned')
scrape_daily_outages(soup, 'electric', 'ClosedIn24Hours')
scrape_daily_outages(soup, 'electric', 'Open')

scrape_daily_outages(soup, 'gas')
