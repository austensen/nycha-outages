from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from random import randint
import time
import os
import re
import csv
import dateparser
from datetime import datetime as dt
from .parsers import *


class History:

    def __init__(self, dir_, start_date, end_date):
        self.start = start_date
        self.end = end_date
        self.dir_ = dir_

        if not os.path.exists(dir_):
            os.makedirs(dir_)

        self.parser = HistoryParser(self.dir_)


    def scrape(self):
        """
        Starts the webdriver, defines wait, starts scraping 
        """
        print('launching browser...')
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 30)

        print('loading webpage...')
        self.driver.get('https://my.nycha.info/Outages/Outages.aspx#tab_history')

        self.wait.until(EC.visibility_of_element_located((By.ID, "fromdatepicker")))
        
        self.get_history_html()

        print('\n' + 'all done!')
        self.driver.quit()

    def get_history_html(self):
        """
        Starts the history scraping process. (Actual scraping of tables done by parse_history_table())

        - inputs date info (could add other options later)
        - downloads history html -- this is what parse_history_table works from (not the live web page)
        """
        self.choose_dates()

        print('searching history...')
        self.driver.find_element_by_css_selector('input.blackbutton').click()

        self.wait.until(EC.visibility_of_element_located((By.ID, 'grvHistoricalOutages')))

        time.sleep(5)

        done = False
        while not done:
            time.sleep(randint(2, 5))

            page_info = self.driver.find_element_by_css_selector('span#ctl00_ContentPlaceHolder1_historicalOutagesList_currentPageInfo.current_page_info').text
            print('scraping pages: ' + page_info, end='\r', flush=True)
            
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            history_table = soup.find(id='grvHistoricalOutages')

            with open(self.dir_ + 'history.html', 'a') as f:
                f.write(str(history_table) + '\n')

            if self.check_exists_by_css_selector('a#ctl00_ContentPlaceHolder1_historicalOutagesList_btnNext.link_buttons'):
                self.driver.find_element_by_css_selector('a#ctl00_ContentPlaceHolder1_historicalOutagesList_btnNext.link_buttons').click()
            else:
                done = True

    def choose_dates(self):
        """
        Assumes dates in YYYY-MM-DD format.
        """
        print('choosing dates...')
        for date in ['start', 'end']:

            if date == 'start':
                date_str = 'fromdatepicker'

            else:
                date_str = 'todatepicker'

            date = "self.{}".format(date)

            if date is not None:
                date_ = dateparser.parse(eval(date)).strftime('%m/%d/%Y')
                element = self.driver.find_element_by_id(date_str)
                element.clear()
                element.send_keys(date_)
            else:
                continue

    def check_exists_by_css_selector(self, css_selector):
        try:
            self.driver.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            return False
        return True
    
    def parse(self):
        self.parser.writer.writeheader()    
        html = open(self.dir_ + 'history.html', 'r').read()
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.select('table#grvHistoricalOutages > tbody > tr')
        for row in rows:
            cells = row.find_all('td', recursive=False)
            # skip header rows with only 'th' and no 'td'
            if not cells:
                continue
            self.parser.parse_cells(cells)


class HistoryParser():

    def __init__(self, dir_):
        self.dir_ = dir_
        self.colnames = [
            'development_name','building_number','address',
            'interruptions','planned','report_date','end_date','outage_duration',
            'buildings_impacted','units_impacted','population_impacted'
        ]
        self.data = dict.fromkeys(self.colnames)
        self.default_data = self.data

        if os.path.exists('history.csv'):
            os.remove('history.csv')

        self.csv_file = open(self.dir_ + 'history.csv', mode='a')
        self.writer = csv.DictWriter(self.csv_file, self.colnames)
        

    def __exit__(self, *args):
        self.csv_file.close()


    def parse_cells(self, cells):
        """
        given a list of cells (<td>), it parses the data out and manages the
        different kinda of rows. for a regular self-contained row it parses all
        the cells and write the row. There are also cases where there is a weird
        nested row format with a 'header' row for the development and some cells
        filled in, then one or more rows following that for each building in the
        development and some of the other rows filled in. So we have to hold
        some of the data from these header row (and not write is as it's own
        row) to combine with the nested rows (and then write each of those
        completed rows). To achieve this we use the self.data and update it as
        we go. 
        """
        if len(cells) == 6:

            if is_nested_header(cells[0]):



                row_type = "header"
                dev, *_ = parse_address_parts(cells[0])

                self.data.update({
                    'development_name': dev
                })
            else:
                row_type = "main"
                dev, bldg, addr = parse_address_parts(cells[0])
                bldgs, units, pop = parse_impact_parts(cells[5])

                self.data.update({
                    'development_name': dev,
                    'building_number': bldg,
                    'address': addr,
                    'buildings_impacted': bldgs,
                    'units_impacted': units,
                    'population_impacted': pop
                })

            interruptions = parse_interuption(cells[1])
            planned = parse_planned(cells[2])
            report_date = parse_datetime(cells[3], '%m/%d/%y %I:%M %p')
            end_date = parse_datetime(cells[4], '%m/%d/%y %I:%M %p')
            outage_duration = end_date - report_date

            self.data.update({
                'interruptions': interruptions,
                'planned': planned,
                'report_date': report_date,
                'end_date': end_date,
                'outage_duration': outage_duration
            })

        elif len(cells) == 2:
            row_type = "nested"
            _, bldg, addr = parse_address_parts(cells[0])
            bldgs, units, pop = parse_impact_parts(cells[1])

            self.data.update({
                'building_number': bldg,
                'address': addr,
                'buildings_impacted': bldgs,
                'units_impacted': units,
                'population_impacted': pop
            })
        else:
            print(cells)
            raise Exception("Row has unexpected structure")

        if row_type == "header":
            return
        elif row_type == "nested":
            self.writer.writerow(self.data)
        elif row_type == "main":
            self.writer.writerow(self.data)
            self.data = self.default_data



