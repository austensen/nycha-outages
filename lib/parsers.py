import csv
import re
import datetime

def parse_address(cell):
    """ Parse table cell for 'Address' into development name, building number, and address """
    # The development and building part is in a div so start there
    dev_bldg_div = cell.find('div')

    dev = re.sub('- Building.*', '', dev_bldg_div.text).strip()

    m = re.search(r'Building (\d+)', dev_bldg_div.text)
    bldg_num = int(m.group(1).replace(',', '')) if m else None

    # Remove the div before extracting the address
    dev_bldg_div.extract()

    address = re.sub(r'[\r\n\s]+', ' ', cell.text).strip()

    return [dev, bldg_num, address]

def parse_address_nobldg(cell):
    """ Same as parse_address but excludes the building number """
    dev, bldg_num, address = parse_address(cell)
    return [dev, address]

def parse_interuption(cell):
    """ Parse table cell for 'Interuption' into comma-separated string of values """
    probs = cell.find_all('span', attrs={'style': 'padding-bottom:5px; display:block; '})
    probs = ', '.join([prob.text.strip() for prob in probs])

    return [probs]

def parse_planned(cell):
    """ Parse table cell for 'Planned' into comma-separated string of values """
    plans = cell.find_all('span', attrs={'style':'padding-bottom:5px; display:block; '})
    plans = ', '.join([plan.text.strip() for plan in plans])

    return [plans]

def parse_datetime(cell):
    """ Parse table cell for 'Reported On' or 'Scheduled Date' into datetime object """
    report_str = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    report_datetime = datetime.datetime.strptime(report_str, '%m/%d/%Y %I:%M %p')

    return [report_datetime]

def parse_date(cell):
    """ Parse table cell with 'mm/dd/yyy' into datetime object """
    report_str = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    report_date = datetime.datetime.strptime(report_str, '%m/%d/%Y')

    return [report_date]

def parse_skip(cell):
    """ Return nothing for a cell that can be skipped entirely """
    return None

def parse_text(cell):
    """ Parse table cell and return just the text """
    return [cell.text.strip()]

def parse_restoration(cell):
    """ Parse table cell for 'Restoration Time' into integer """
    m = re.search(r'(\d+) Hours', cell.text)
    restore_hours = int(m.group(1).replace(',', '')) if m else None

    return [restore_hours]

def parse_status(cell):
    """ Parse table cell for 'Status' into string """
    # extra definition of value can be removed
    span = cell.find('span')
    span.extract()

    status = re.sub(r'[\s\r\n]+', ' ', cell.text).strip()
    return [status]

def parse_impact(cell):
    """ Parse table cell for 'Impact' into buildings, units, and population """
    bldgs, units, pop = [int(x.text.strip().replace(',', '')) for x in cell.find_all('td')]

    return [bldgs, units, pop]

def get_col_info(service, outage):
    """ For a given service type and outage period get the parsing info for the table """
    if service == 'gas':
        col_names=[
            'development_name', 'building_number', 'address',
            'reported_datetime',
            'buildings', 'units', 'population'
        ]
        parsers=[
            parse_address_nobldg,
            parse_skip,
            parse_skip,
            parse_date,
            parse_text
        ]
    elif outage == 'Planned':
        col_names=[
        'development_name', 'building_number', 'address',
        'interruptions',
        'scheduled_datetime',
        'buildings', 'units', 'population'
        ]
        parsers=[
            parse_address,
            parse_interuption,
            parse_datetime,
            parse_impact
        ]
    elif outage == 'ClosedIn24Hours':
        col_names=[
            'development_name', 'building_number', 'address',
            'interruptions',
            'planned',
            'reported_datetime',
            'restoration_hours',
            'buildings', 'units', 'population'
        ]
        parsers=[
            parse_address,
            parse_interuption,
            parse_planned,
            parse_datetime,
            parse_restoration,
            parse_impact
        ]
    elif outage == 'Open':
        col_names=[
            'development_name', 'building_number', 'address',
            'interruptions',
            'planned',
            'reported_datetime',
            'status',
            'buildings', 'units', 'population'
        ]
        parsers=[
            parse_address,
            parse_interuption,
            parse_planned,
            parse_datetime,
            parse_status,
            parse_impact
        ]
    else:
        print("'outage' must be one of ['Planned', 'Open', 'ClosedIn24Hours']")

    return col_names, parsers


def get_published_date(soup, service):
    """ Get the date the data was published as a string for use in filename """
    box_id = f'ctl00_ContentPlaceHolder1_{service}OutagesList_grayboxPanel'
    box_text = soup.find(id=box_id).text.strip()
    match = re.search(r'(\w+ \d{1,2}, \d{4} at \d{1,2}:\d{1,2} [AP]M)', box_text)
    pub_date = datetime.datetime.strptime(match.group(1), '%B %d, %Y at %I:%M %p')
    return pub_date.strftime("%Y-%m-%d_%H-%M")

def scrape_table(soup, service, outage=''):
    """ For a given service and outage period parse the data table and save as CSV """

    table_id =  f'ctl00_ContentPlaceHolder1_{service}OutagesList_grvOutages{outage}'

    # There is now speicif publish date on the gas tab
    if service == 'gas':
        pub_date = get_published_date(soup, 'heatHotWater')
    else: 
        pub_date = get_published_date(soup, service)

    filename = f'{pub_date}_{service}_{outage}.csv' if outage else f'{pub_date}_{service}.csv'

    col_names, parsers = get_col_info(service, outage)

    file = open(f'data/{filename}', 'w+')

    writer = csv.writer(file)
    writer.writerow(col_names)

    table = soup.find(id=table_id)

    # If there is nothing to report the table doesn't exist, so skip
    if not table:
        return

    rows = table.find_all('tr', recursive=False)

    data = []
    for row in rows:
        cols = row.find_all('td', recursive=False)

        # first row is header, and has only 'th' and no 'td'
        if not cols:
            continue

        # confirm there is a parser for each column
        if not len(cols) == len(parsers):
            print('number of parser functions not equal to number of columns')
            return

        out_row = []
        for i in range(len(parsers)):
            vals = parsers[i](cols[i])
            if vals:
                out_row += vals

        data.append(out_row)

    writer.writerows(data)
