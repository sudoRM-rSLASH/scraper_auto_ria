import requests
import sqlite3
import pytz
import re

from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup

tz_here = pytz.timezone("Europe/Kiev")


@dataclass
class Regulars:
    objem: str = r"\d[.]\d\d?\sл\s? | \d\sл\s?"
    korobka: str = r"(?i)(\W|^)(Автомат|Ручна\s[/]\sМеханіка|Варіатор)(\W|$)"
    toplivo: str = r"(?i)(\W|^)(Бензин|Дизель|Електро|Газ\s/\sБензин|Гiбрид)(\W|$)"


class Parser(object):
    def __init__(self, url: str, page_count: int, header: str):
        self.url = url
        self.page_count = page_count
        self.header = header
        self.cars = []
        self.cars_urls = {}
        self.dates = []
        self.content = []
        self.list_with_cars = []

    def start(self):
        print(f'start at {datetime.now(tz=tz_here).strftime("%Y-%m-%d %H:%M")}')
        self.get_all_pages()
        self.get_cars_urls()
        self.get_all_info()
        self.bulk_create_db()
        print(f'finished at {datetime.now(tz=tz_here).strftime("%Y-%m-%d %H:%M")}')

    def get_all_pages(self):
        for page in range(0, self.page_count):
            url = self.url + f"page={page}&size=10"
            req = requests.get(url, headers=self.header)
            content = BeautifulSoup(req.text, "html.parser")
            cars = content.find_all("div", class_="content-bar")
            self.cars += list(cars)

    def get_cars_urls(self):
        for result_set in self.cars:
            url = result_set.find("a", class_="m-link-ticket").attrs.get("href")
            data = result_set.find("div", class_="footer_ticket").find("span").attrs
            self.cars_urls[f"{url}"] = data

    def get_all_info(self):
        for url, data in self.cars_urls.items():
            req = requests.get(url, headers=self.header)
            content = BeautifulSoup(req.text, "html.parser")

            self.list_with_cars.append(
                Serializer(content=content, data=data, url=url).start()
            )

    def bulk_create_db(self):
        Database(list_with_cars=self.list_with_cars).save_data()


class Serializer(object):
    def __init__(self, content: BeautifulSoup, data: str, url: str):
        self.content = content
        self.data = data
        self.url = url
        self.name_model_year = None
        self.probeg = None
        self.city = None
        self.tech_info = None
        self.probeg_per_year = None
        self.objem = None
        self.korobka = None
        self.toplivo = None
        self.nomer = None
        self.vin = None
        self.opisanie = None
        self.price_usd = None
        self.price_uah = None
        self.current_car = {}
        self.car_tuple = None

    def start(self):
        self.get_name_model_year()
        self.get_probeg()
        self.get_city()
        self.get_technical_info()
        self.get_probeg_per_year()
        self.get_engine_info()
        self.get_registration_info()
        self.get_opisanie()
        self.get_prices()
        self.create_dict()
        self.to_tuple()
        return self.car_tuple

    def get_name_model_year(self):
        try:
            self.name_model_year = str(
                self.content.find("h1", class_="head").text
            ).split(" ")
        except AttributeError:
            self.name_model_year = None

    def get_probeg(self):
        try:
            self.probeg = (
                self.content.find("div", class_="technical-info", id="details")
                .find("dd", class_="mhide")
                .find("span", class_="argument")
                .text
            )
        except AttributeError:
            self.probeg = None

    def get_city(self):
        try:
            self.city = self.content.find("div", class_="item_inner").text
        except AttributeError:
            self.city = None

    def get_technical_info(self):
        try:
            self.tech_info = self.content.find(
                "div", class_="technical-info", id="details"
            ).text
            self.tech_info = self.tech_info.replace("•", " ").split(" ")
            self.tech_info = str.join(" ", self.tech_info)
        except AttributeError or ValueError:
            self.tech_info = None

    def get_probeg_per_year(self):
        try:
            self.probeg_per_year = round(
                int(self.probeg.split(" ")[0])
                / (int(datetime.now().year) - int(self.name_model_year[-1])),
                2,
            )
        except ValueError:
            self.probeg_per_year = None
        except ZeroDivisionError:
            self.probeg_per_year = round(int(self.probeg.split(" ")[0]) / 1, 2)

    def get_engine_info(self):
        try:
            self.objem = re.search(Regulars.objem, str(self.tech_info)).group(0)
        except AttributeError:
            self.objem = None
        try:
            self.korobka = re.search(Regulars.korobka, str(self.tech_info)).group(0)
        except AttributeError:
            self.korobka = None
        try:
            self.toplivo = re.search(Regulars.toplivo, str(self.tech_info)).group(0)
        except AttributeError:
            self.toplivo = None

    def get_registration_info(self):
        try:
            self.nomer = (
                self.content.find("div", class_="t-check")
                .find("span", class_="state-num ua")
                .text
            )
        except AttributeError:
            self.nomer = "X X X X"
        try:
            self.vin = (
                self.content.find("div", class_="t-check")
                .find("span", class_="label-vin")
                .text
            )
        except AttributeError:
            try:
                self.vin = (
                    self.content.find("div", class_="t-check")
                    .find("span", class_="vin-code")
                    .text
                )
            except AttributeError:
                self.vin = None

    def get_opisanie(self):
        try:
            self.opisanie = self.content.find("div", class_="full-description").text
        except AttributeError:
            self.opisanie = None

    def get_prices(self):
        try:
            self.price_usd = (
                self.content.find("section", class_="price mb-15 mhide")
                .find("div", class_="price_value")
                .find("strong")
                .text
            )
        except ValueError:
            self.price_usd = None
        try:
            self.price_uah = (
                int(str.join("", self.price_usd.replace("$", "").split())) * 40.56
            )
        except ValueError:
            self.price_uah = self.price_usd

    def create_dict(self):
        self.current_car = {
            "id": self.url.split(".html")[0].split("_")[-1],
            "marka": self.name_model_year[0],
            "model": str.join(
                " ", self.name_model_year[1 : len(self.name_model_year) - 1]
            ),
            "year": self.name_model_year[-1],
            "probeg": self.probeg,
            "probeg_per_year": f"{self.probeg_per_year} тис.км / рiк",
            "city": self.city,
            "korobka": self.korobka,
            "toplivo": self.toplivo,
            "objem": self.objem,
            "nomer": str.join(" ", self.nomer.split()[0:3]),
            "vin": self.vin,
            "opisanie": self.opisanie,
            "data_objavi": self.data.get("data-add-date"),
            "price_usd": self.price_usd,
            "price_uah": self.price_uah,
            "url": self.url,
        }

    def to_tuple(self):
        self.car_tuple = tuple(self.current_car.values())


class Database(object):
    def __init__(self, list_with_cars: list):
        self.list_with_cars = list_with_cars
        self.db = sqlite3.connect("cars1_data.db")
        self.cur = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS cars(
                    id INTEGER PRIMARY KEY ,
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
                    """
        )

    def save_data(self):
        self.cur.executemany(
            "INSERT OR REPLACE INTO cars(id, "
            "marka, model, year, probeg, probeg_per_year,"
            "city, korobka, toplivo, objem, nomer, vin,"
            "opisanie, data_objavi, price_usd, price_uah, url)"
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            self.list_with_cars,
        )
        self.db.commit()

    def __del__(self):
        self.db.close()
