import requests
import sqlite3
import pytz
from bs4 import BeautifulSoup
from datetime import datetime
from serializer import serialize, serialize_
from serializer import car_list, cars_1



class BigClass(object):
    cars_urls = {}
    dates_ = []
    cars = ''
    tz_here = pytz.timezone("Europe/Kiev")

    def __init__(self, url, page_count, header):
        self.url = url
        self.page_count = page_count
        self.header = header


    def get_all_cars(self):

        print(f'start at {datetime.now(tz=self.tz_here).strftime("%Y-%m-%d %H:%M")}')
        for page in range(0, self.page_count):
            url = self.url + f'page={page}&size=30'
            req = requests.get(url,
                               headers=self.header)
            content = BeautifulSoup(req.text, "html.parser")
            cars = content.findAll('div', class_="content-bar")
            self.cars = cars
            for car_url in self.cars:
                car_name = car_url.find('span', class_="blue bold").text
                url = car_url.find('a', class_="m-link-ticket").attrs.get("href")
                data = car_url.find('div', class_="footer_ticket").find('span').attrs
                self.dates_ = data
                self.cars_urls[f'{car_name}'] = url

    def get_all_info(self):
        for url in self.cars_urls.values():
            req = requests.get(url,
                               headers=self.header)
            content = BeautifulSoup(req.text, "html.parser")
            serialize(content=content, data=self.dates_, url=url)

    def get_serialized_content(self):
        car_list_ = car_list
        serialize_(car_list_)

    def create_db(self):
        db = sqlite3.connect('cars1_data.db')

        cur = db.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS cars(
        id_objavi INTEGER PRIMARY KEY,
        marka TEXT,
        model TEXT,
        year TEXT,
        probeg TEXT,
        probeg_per_year TEXT,
        city TEXT,
        korobka TEXT,
        toplivo TEXT,
        objem TEXT,
        nomer TEXT NULL,
        vin TEXT NULL,
        opisanie TEXT,
        data_objavi TEXT,
        price_usd TEXT,
        price_uah TEXT,
        url TEXT)
        """)
        cur.executemany('INSERT INTO cars('
                        'marka, model, year, probeg, probeg_per_year,'
                        'city, korobka, toplivo, objem, nomer, vin,'
                        'opisanie, data_objavi, price_usd, price_uah, url)'
                        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', cars_1)
        db.commit()
        db.close()
        print(f'finished at {datetime.now(tz=self.tz_here).strftime("%Y-%m-%d %H:%M")}')

