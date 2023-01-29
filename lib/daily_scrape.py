import os 
import csv
import scraperwiki

from .parsers import PARSE_COL_FUNCTIONS, parse_gas_cols,  

def scrape_daily_outages(soup, service_type, service_status = ''):

    # Depending on table to be parsed, set the table ID and parsing function
    if service_type == 'gas':
        div_id = 'ctl00_ContentPlaceHolder1_gasOutagesList_panData'
        table_id = 'ctl00_ContentPlaceHolder1_gasOutagesList_grvOutages'
        parse_cols = parse_gas_cols
    else:
        if service_status == 'ClosedIn24Hours':
            div_id = 'ctl00_ContentPlaceHolder1_' + service_type + 'OutagesList_panOutages' + service_status
            table_id = 'grvOutages' + service_status
        if service_status == 'Planned':
            div_id = 'ctl00_ContentPlaceHolder1_' + service_type + 'OutagesList_pan' + service_status + 'Outages'
            table_id = 'grv' + service_status + 'Outages'
        if service_status == 'Open':
            div_id = 'ctl00_ContentPlaceHolder1_' + service_type + 'OutagesList_pan' + service_status + 'Outages'
            table_id = 'grvOutages' + service_status
        parse_cols = PARSE_COL_FUNCTIONS[service_status]

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

        pk_cols = ['development_name', 'address', 'interruptions', 'status', 'reported_scheduled']
        scraperwiki.sqlite.save(unique_keys=pk_cols, data=data)
