import requests
import os
from bs4 import BeautifulSoup

from lib.parsers import scrape_outages

URL = 'https://my.nycha.info/Outages/Outages.aspx'
page = requests.get(URL)
content = page.content
soup = BeautifulSoup(content, 'html.parser')


def parse_history_cols(cols):

    dev, bldg, addr = parse_address_parts(cols[0]) # this column is the same in the history tab
    gas_lines = None # this column does not exist in history tab
    gas_restored_on = None # this column does not exist in history tab
    interruptions = parse_interuption(cols[1]) # this column is the same in the history tab
    planned = parse_planned(cols[2]) # this column is the same in the history tab
    reported_scheduled = parse_reported(cols[3]) # added this as a col b/c I think we'll want to know when it was reported
    restoration_time = parse_restoration(cols[4]) # changed from 3 to 4
    status = 'Restored' # kept the same b/c history == it's been restored
    bldgs, units, pop = parse_impact_parts(cols[5]) # this column is the same in the history tab
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
