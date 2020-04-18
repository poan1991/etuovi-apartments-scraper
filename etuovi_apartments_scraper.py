'''
Created on 28.01.2020
@Authors poan1991 (https://github.com/poan1991) & Nsantis (https://github.com/Nsantis/)
'''
import re
import time
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openpyxl.utils.dataframe import dataframe_to_rows
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from openpyxl import Workbook
from openpyxl.cell.cell import WriteOnlyCell
import datetime
import numpy as np

class apartments_webscraper():
    def __init__(self, city, price_max, price_min, size_max, size_min):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.COUNT = 0
        self.city = city
        self.price_max = price_max
        self.price_min = price_min
        self.size_max = size_max
        self.size_min = size_min

    def search_apartments(self):
        driver = self.driver
        driver.get("https://www.etuovi.com/myytavat-asunnot")
        driver.implicitly_wait(10)
        accept = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div[1]/button')
        accept.click()
        modify_search = driver.find_element_by_xpath('//*[text()="Muokkaa hakua"]')
        modify_search.click()
        driver.implicitly_wait(60)
        location = driver.find_element_by_xpath('//*[@id="location"]')
        location.send_keys(self.city)
        location.send_keys(Keys.ENTER)
        max_price_field = driver.find_element_by_xpath('//*[@id="priceMax"]')  # Max apartment price
        max_price_field.send_keys(self.price_max)
        min_price_field = driver.find_element_by_xpath('//*[@id="priceMin"]')  # Min apartment price
        min_price_field.send_keys(self.price_min)
        size_min_field = driver.find_element_by_xpath('//*[@id="sizeMin"]')
        size_min_field.send_keys(self.size_min)
        size_max_field = driver.find_element_by_xpath('//*[@id="sizeMax"]')
        size_max_field.send_keys(self.size_max)
        show_apartments = driver.find_element_by_xpath('//*[@id="searchButton"]')
        show_apartments.click()
        time.sleep(1)

    @property
    def next_page(self):
        driver = self.driver
        try:
            lastpage = driver.find_element_by_xpath('//*[@id="pagination"]/div[5]/button').text
            lastpage = int(lastpage)
        except:
            try:
                lastpage = driver.find_element_by_xpath('//*[@id="pagination"]/div[4]/button').text
                lastpage = int(lastpage)
            except:
                try:
                    lastpage = driver.find_element_by_xpath('//*[@id="pagination"]/div[3]/button').text
                    lastpage = int(lastpage)
                except:
                    try:
                        lastpage = driver.find_element_by_xpath('//*[@id="pagination"]/div[2]/button').text
                        lastpage = int(lastpage)
                    except:
                        try:
                            lastpage = driver.find_element_by_xpath('//*[@id="pagination"]/div[1]/button').text
                            lastpage = int(lastpage)
                        except:
                            print("Error lastpage")

        page = list(range(lastpage))
        dataOut = list()
        for i in range(len(page)):
            self.COUNT = self.COUNT + 1
            URL = str(driver.current_url) + "&sivu=" + str(self.COUNT)
            print(URL)
            headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            for tag in soup.find_all(attrs={"class": "styles__cardTitle__14F5m"}):
                x1 = (re.sub('(check|Hinta|m²Vuosi)', '; ', tag.get_text()))
                x2 = (re.sub('€Koko', ': ', x1))
                x3 = (re.sub('\s+;', ';', x2))
                x4 = (re.sub(',,', ',', x3))
                x5 = (re.sub('Tarjouskauppa', '', x4))
                x6 = (re.sub('(€arrow_downward.*:|€arrow_upward.*:|; |: )', ';', x5))
                x7_list = x6.split(";")
                x8_list = [re.sub('\xa0', '', i) for i in x7_list]
                dataOut.append(x8_list)
        df = pd.DataFrame(dataOut)
        try:
            df.columns = ['Description', 'Address', 'Price', 'Size', 'Year', 'None']
            del df['None']
        except:
            try:
                df.columns = ['Description', 'Address', 'Price', 'Size', 'Year', 'None', 'None1']
                del df['None']
                del df['None1']
            except:
                try:
                    df.columns = ['Description', 'Address', 'Price', 'Size', 'Year']
                except:
                    print('ERROR column')

        df = df[~df.Year.astype(str).str.contains("Viimeisin tarjous:Tarjous")]
        df['Price'] = df['Price'].str.replace(',', '.')
        df['Size'] = df['Size'].str.replace(',', '.')
        df['Year'] = df['Year'].str.replace('-', '0')
        df['Year'] = df['Year'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int).dropna()
        df['Price'] = df['Price'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float).dropna()
        df['Size'] = df['Size'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float).dropna()
        df['Price_per_m2'] = df['Price'] / df['Size']
        try:
            df['Price_per_m2'] = df['Price_per_m2'].round(1).astype(int)
            df['Price_per_m2'] = df['Price_per_m2'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int).dropna()
        except:
            df['Price_per_m2'] = df['Price_per_m2'].round(1)
            df['Price_per_m2'] = df['Price_per_m2'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float).dropna()
            df = df[df.Price_per_m2 != np.inf]
            df['Price_per_m2'] = df['Price_per_m2'].replace([np.inf, -np.inf], np.nan).dropna(axis=0)
            df = df[df.Price_per_m2 != 0.0]

        pd.set_option('display.width', None)
        pd.set_option('display.max_rows', None)
        print(df)
        driver.close()
        return df

    def save_to_excel(self, df):
        Current_Time = datetime.datetime.today()
        Date = str(Current_Time)[:-10].strip()
        city = self.city
        wb = Workbook(write_only=True)
        ws = wb.create_sheet()

        cell = WriteOnlyCell(ws)
        cell.style = 'Pandas'

        def format_first_row(row, cell):

            for c in row:
                cell.value = c
                yield cell

        rows = dataframe_to_rows(df)
        first_row = format_first_row(next(rows), cell)
        ws.append(first_row)
        for row in rows:
            row = list(row)
            cell.value = row[0]
            row[0] = cell
            ws.append(row)

        wb.save(str(city)+"_apartment_search_"+str(Date)+".xlsx")

#input search parameter values here = (city, price_max, price_min, size_max, size_min)
search = apartments_webscraper('Rovaniemi', '100', '1', '100', '20')


if __name__ == "__main__":
    apt = apartments_webscraper(search.city, search.price_max, search.price_min, search.size_max, search.size_min)
    apt.search_apartments()
    dataOut = apt.next_page
    apt.save_to_excel(dataOut)
    print('Done')

    dataOut.groupby('Year')['Address'].nunique().plot(kind='bar')
    plt.title('The age of apartments for sale')
    plt.ylabel('Number of apartments for sale')
    plt.xlabel('Construction year')
    plt.grid()


    dataOut[['Size']].plot(kind='hist', bins=10)
    plt.title('The size of the apartment')
    plt.ylabel('Number of apartments for sale')
    plt.xlabel('Size m2')
    plt.grid()


    dataOut[['Price_per_m2']].plot(kind='hist', bins=10)
    plt.title('The price of apartment per m^2')
    plt.ylabel('Number of apartments for sale')
    plt.xlabel('Price per m2')
    plt.grid()
    plt.show()

