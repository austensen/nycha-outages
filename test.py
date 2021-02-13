import requests
import os
from bs4 import BeautifulSoup

from lib.parsers import scrape_outages

URL = 'https://my.nycha.info/Outages/Outages.aspx'
page = requests.get(URL)
content = page.content
soup = BeautifulSoup(content, 'html.parser')

# defining items for def parse_history_cols(cols)
# deleted parse_address_parts_gas, parse_status_restored_gas, parse_date
# because these were all related to the gas table.
# deleted parse_status because it was an extra definition and history tab
# should only have things that are restore.
# deleted parse_restoration because the history tab has a date/time end date
# rather than an integer for restoration hours

import re
import datetime

def parse_address_parts(cell):
    """ Parse table cell for 'Address' into development name, building number, and address """
    # The development and building part is in a div so start there
    dev_bldg_div = cell.find('div')

    dev = re.sub('(- Building|- Entire Development).*', '', dev_bldg_div.text).strip()

    m = re.search(r'Building (\d+)', dev_bldg_div.text)
    bldg_num = int(m.group(1).replace(',', '')) if m else None

    # Remove the div before extracting the address
    dev_bldg_div.extract()

    address = re.sub(r'[\r\n\s]+', ' ', cell.text).strip()

    return dev, bldg_num, address

def parse_interuption(cell):
    """ Parse table cell for 'Interruption' into comma-separated string of values """
    probs = cell.find_all('span', attrs={'style': 'padding-bottom: 5px; display: block;'})
    # probs = probs.find_all
    probs = ', '.join([prob.text.strip() for prob in probs])

    return probs

def parse_planned(cell):
    """ Parse table cell for 'Planned' into comma-separated string of values """
    plans = cell.find_all('span', attrs={'style':'padding-bottom: 5px; display: block;'})
    plans = ', '.join([plan.text.strip() for plan in plans])

    return plans

def parse_datetime(cell):
    """ Parse table cell for 'Reported On' or 'Scheduled Date' into datetime object """
    report_str = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    report_datetime = datetime.datetime.strptime(report_str, '%m/%d/%Y %I:%M %p')

    return report_datetime

def parse_skip(cell):
    """ Return nothing for a cell that can be skipped entirely """
    return None

def parse_text(cell):
    """ Parse table cell and return just the text """
    return cell.text.strip()

def parse_impact_parts(cell):
    """ Parse table cell for 'Impact' into buildings, units, and population """
    bldgs, units, pop = [int(x.text.strip().replace(',', '')) for x in cell.find_all('td')]

    return [bldgs, units, pop]

# make parse_history_cols
import pytz
def parse_history_cols(cols):

    dev, bldg, addr = parse_address_parts(cols[0])
    interruptions = parse_interuption(cols[1])
    planned = parse_planned(cols[2])
    reported_date = parse_datetime(cols[3])
    restored_date = parse_datetime(cols[4])
    status = 'Restored' # history == it's been restored
    bldgs, units, pop = parse_impact_parts(cols[5])
    imported_on = datetime.datetime.now(pytz.timezone('America/New_York'))

    data = {
        'development_name': dev,
        'building_number': bldg,
        'address': addr,
        'gas_lines': gas_lines, # can we delete this since it's None?
        'interruptions': interruptions,
        'planned': planned,
        'gas_restored_on': gas_restored_on, # can we delete this since it's None?
        'reported_scheduled': reported_scheduled,
        'restoration_time': restoration_time,
        'status': status,
        'buildings_impacted': bldgs,
        'units_impacted': units,
        'population_impacted': pop,
        'imported_on': imported_on
    }

    return data

div_id = 'ctl00_ContentPlaceHolder1_historicalOutagesList_UpdatePanel1'
table_id = 'grvHistoricalOutages'
table_div = soup.find(id=div_id)
table = table_div.find(id=table_id)


rows = table.find_all('tr', recursive=False)

for row in rows:
    cols = row.find_all('td', recursive=False)

    # first row is header, and has only 'th' and no 'td'
    if not cols:
        continue

    data = parse_history_cols(cols)

    # write row to a csv
    import csv
    with open('nycha_history', mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, data.keys())
        writer.writeheader()
        writer.writerow(data)
