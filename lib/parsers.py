import csv
import re
import datetime
import pytz
import scraperwiki

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

def parse_address_parts_gas(cell):
    """ Parse the 'Address' column in the Gas table giving development, address, and gas_lines """

    # The development is in the first div and there are no building numbers
    dev_div = cell.find('div')
    dev = dev_div.text.strip()

    # Remove the development then get the nested divs. The last one is the gas lines, the first one is empty
    dev_div.extract()
    sub_divs = cell.find('div').find_all('div')

    gas_lines = sub_divs[1].text.strip()

    # Remove both of these nested divs and then all that remains is the address
    for div in sub_divs:
        div.extract()

    addr = cell.text.strip()

    return dev, addr, gas_lines

def parse_interuption(cell):
    """ Parse table cell for 'Interruption' into comma-separated string of values """
    probs = cell.find_all('span', attrs={'style': 'padding-bottom:5px; display:block; '})
    probs = ', '.join([prob.text.strip() for prob in probs])

    return probs

def parse_planned(cell):
    """ Parse table cell for 'Planned' into comma-separated string of values """
    plans = cell.find_all('span', attrs={'style':'padding-bottom:5px; display:block; '})
    plans = ', '.join([plan.text.strip() for plan in plans])

    return plans

def parse_datetime(cell):
    """ Parse table cell for 'Reported On' or 'Scheduled Date' into datetime object """
    report_str = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    report_datetime = datetime.datetime.strptime(report_str, '%m/%d/%Y %I:%M %p')

    return report_datetime

def parse_date(cell):
    """ Parse table cell with 'mm/dd/yyy' into datetime object """
    report_str = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    report_date = datetime.datetime.strptime(report_str, '%m/%d/%Y')

    return report_date

def parse_skip(cell):
    """ Return nothing for a cell that can be skipped entirely """
    return None

def parse_text(cell):
    """ Parse table cell and return just the text """
    return cell.text.strip()

def parse_restoration(cell):
    """ Parse table cell for 'Restoration Time' into integer """
    m = re.search(r'(\d+) Hours', cell.text)
    restore_hours = int(m.group(1).replace(',', '')) if m else None

    return restore_hours

def parse_status(cell):
    """ Parse table cell for 'Status' into string """
    # extra definition of value can be removed
    span = cell.find('span')
    span.extract()

    status = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    return status

def parse_status_restored_gas(cell):
    """ Parse 'Est. Completion' column into status and gas_restored_on """
    text = cell.text.strip()
    match = re.search(r'\d{1,2}/\d{1,2}\d{4}', text)
    if match:
        restored_str = match.group(1)
        restored_date = datetime.datetime.strptime(restored_str, '%m/%d/%Y')
        status = 'Restored'
    else:
        restored_date = None
        status = 'In Progress'

    return status, restored_date


def parse_impact_parts(cell):
    """ Parse table cell for 'Impact' into buildings, units, and population """
    bldgs, units, pop = [int(x.text.strip().replace(',', '')) for x in cell.find_all('td')]

    return [bldgs, units, pop]



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


def parse_planned_cols(cols):

    dev, bldg, addr = parse_address_parts(cols[0])
    gas_lines = None
    gas_restored_on = None
    interruptions = parse_interuption(cols[1])
    planned = 'Planned'
    reported_scheduled = parse_datetime(cols[2])
    restoration_time = None
    status = 'Planned'
    bldgs, units, pop = parse_impact_parts(cols[3])
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



def parse_ongoing_cols(cols):

    dev, bldg, addr = parse_address_parts(cols[0])
    gas_lines = None
    gas_restored_on = None
    interruptions = parse_interuption(cols[1])
    planned = parse_planned(cols[2])
    reported_scheduled = parse_datetime(cols[3])
    restoration_time = None
    status = parse_status(cols[4])
    bldgs, units, pop = parse_impact_parts(cols[5])
    imported_on = datetime.datetime.now(pytz.timezone('America/New_York'))

    data = {
        'development_name': dev, 
        'building_number': bldg, 
        'address': addr,
        'gas_lines': gas_lines,
        'interruptions': interruptions,
        'planned': planned,
        'reported_scheduled': reported_scheduled,
        'gas_restored_on': gas_restored_on,
        'restoration_time': restoration_time,
        'status': status,
        'buildings_impacted': bldgs, 
        'units_impacted': units, 
        'population_impacted': pop,
        'imported_on': imported_on
    }

    return data


def parse_gas_cols(cols):

    dev, addr, gas_lines = parse_address_parts_gas(cols[0])
    bldg = None
    interruptions = 'Gas'
    planned = None
    reported_scheduled = parse_date(cols[3])
    restoration_time = None
    status, gas_restored_on = parse_status_restored_gas(cols[4])
    bldgs, units, pop = [None, None, None]
    imported_on = datetime.datetime.now(pytz.timezone('America/New_York'))

    data = {
        'development_name': dev, 
        'building_number': bldg, 
        'address': addr,
        'gas_lines': gas_lines,
        'interruptions': interruptions,
        'planned': planned,
        'reported_scheduled': reported_scheduled,
        'gas_restored_on': gas_restored_on,
        'restoration_time': restoration_time,
        'status': status,
        'buildings_impacted': bldgs, 
        'units_impacted': units, 
        'population_impacted': pop,
        'imported_on': imported_on
    }

    return data

PARSE_COL_FUNCTIONS = {
    'Open': parse_ongoing_cols,
    'Planned': parse_planned_cols,
    'ClosedIn24Hours': parse_restored_cols
}

def scrape_outages(soup, service_type, service_status = ''):

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
        print('test')
