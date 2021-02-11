import requests
import os
from bs4 import BeautifulSoup

from lib.parsers import scrape_outages

URL = 'https://my.nycha.info/Outages/Outages.aspx'
page = requests.get(URL)
content = page.content
soup = BeautifulSoup(content, 'html.parser')


def parse_restored_cols(cols):

    dev, bldg, addr = parse_address_parts(cols[0])
    gas_lines = None
    gas_restored_on = None
    interruptions = parse_interuption(cols[1])
    planned = parse_planned(cols[2])
    reported_scheduled = None
    restoration_time = parse_restoration(cols[3])
    status = 'Restored'
    bldgs, units, pop = parse_impact_parts(cols[4])
    imported_on = datetime.datetime.now(pytz.timezone('America/New_York'))

    data = {
        'development_name': dev, 
        'building_number': bldg, 
        'address': addr,
        'gas_lines': gas_lines,
        'interruptions': interruptions,
        'planned': planned,
        'gas_restored_on': gas_restored_on,
        'reported_scheduled': reported_scheduled,
        'restoration_time': restoration_time,
        'status': status,
        'buildings_impacted': bldgs, 
        'units_impacted': units, 
        'population_impacted': pop,
        'imported_on': imported_on
    }

    return data



table_div = soup.find(id=div_id)
table = table_div.find(id=table_id)

# If there is nothing to report the table doesn't exist, so skip
if not table:
    return

rows = table.find_all('tr', recursive=False)

for row in rows:
    cols = row.find_all('td', recursive=False)

    # first row is header, and has only 'th' and no 'td'
    if not cols:
        continue

    data = parse_cols(cols)

    # write row to a csv