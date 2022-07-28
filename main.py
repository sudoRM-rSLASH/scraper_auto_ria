import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
num_ = 0
cars_urls = {}
cars_list = []
for page in range(1, 5):
    url = 'https://auto.ria.com/uk/car/used/' + f'?page={page}'
    req = requests.get(url,
                       headers={
                           "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                       })
    content = BeautifulSoup(req.text, "html.parser")
    cars = content.findAll('div', class_="content-bar")
    data = content.find('div', class_="footer_ticket").find('span').attrs

    for car_url in cars:
        car_name = car_url.find('span', class_="blue bold").text
        url = car_url.find('a', class_="m-link-ticket").attrs.get("href")
        cars_urls[f'{car_name}'] = url
print(cars_urls)
for urls in cars_urls.values():
    num_ += 1
    all_car_info = []
    url = urls
    req = requests.get(url,
                       headers={
                           "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                       })
    content = BeautifulSoup(req.text, "html.parser")
    name_model_year = str(content.find('h1', class_="head").text).split(' ')
    probeg = content.find('div', class_="technical-info", id="details").find('dd', class_="mhide").find(
        'span', class_="argument").text
    try:
        probeg_per_year = int(probeg.split(' ')[0]) / (int(datetime.now().year) - int(name_model_year[-1]))
    except ZeroDivisionError:
        probeg_per_year = int(probeg.split(' ')[0]) / 1
    city = content.find('div', class_="item_inner").text
    tech_info = content.find('div', class_="technical-info", id="details").text
    tech_info = tech_info.replace('•', ' ').split(' ')
    tech_info = str.join(' ', tech_info)
    try:
        objem = re.search(r'\d[.]\d\d?\sл\s? | \d\sл\s?', str(tech_info)).group(0)
    except AttributeError:
        objem = re.search(r'\d[.]\d\d?\sл\s? | \d\sл\s?', str(tech_info))
        korobka = re.search(r'(?i)(\W|^)(Автомат|Механiка\s/\sРучна)(\W|$)', str(tech_info))
    try:
        korobka = re.search(r'(?i)(\W|^)(Автомат|Ручна\s/\sМеханiка)(\W|$)', str(tech_info)).group(0)
    except AttributeError:
        korobka = re.search(r'(?i)(\W|^)(Автомат|Механiка\s/\sРучна)(\W|$)', str(tech_info))
    try:
        toplivo = re.search(
            r'(?i)(\W|^)(Бензин|Дизель|Електро|Газ\s/\sБензин|Гiбрид)(\W|$)'
            , str(tech_info)).group(0)
    except AttributeError:
        toplivo = re.search(r'(?i)(\W|^)(Бензин|Дизель|Електро|Газ\s/\sБензин|Гiбрид)(\W|$)', str(tech_info))
    try:
        nomer = content.find('div', class_="t-check").find('span', class_="state-num ua").text
    except AttributeError:
        nomer = 'X X X X'
    try:
        vin = content.find('div', class_="t-check").find('span', class_="label-vin").text
    except AttributeError:
        try:
            vin = content.find('div', class_="t-check").find('span', class_="vin-code").text
        except AttributeError:
            vin = None
    try:
        opisanie = content.find('div', class_="full-description").text
    except AttributeError:
        opisanie = None
    price_usd = content.find(
        'section', class_="price mb-15 mhide").find('div', class_="price_value").find('strong').text
    price_uah = int(str.join('', price_usd.replace('$', '').split())) * 40.56
    current_car = {
        "id": num_,
        "marka": name_model_year[0],
        "model": str.join(' ', name_model_year[1: len(name_model_year) - 1]),
        "year": name_model_year[-1],
        "probeg": probeg,
        "probeg_per_year": f'{round(probeg_per_year, 2)} тис.км / рiк',
        "city": city,
        "korobka": korobka,
        "toplivo": toplivo,
        "objem": objem,
        "nomer": str.join(' ', nomer.split()[0: 3]),
        "vin": vin,
        "opisanie": opisanie,
        "data_objavi": data.get('data-add-date'),
        "price_usd": price_usd,
        "price_uah": price_uah
        }
    cars_list.append(current_car)
print(cars_list)
cars_1 = []
for car in cars_list:
    tuple_ = tuple(car.values())
    cars_1.append(tuple_)
print(cars_1)

db = sqlite3.connect('cars_data.db')

cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS cars(
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
marka TEXT,
model TEXT,
year INTEGER,
probeg INTEGER,
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
price_uah TEXT)
""")
cur.executemany('INSERT INTO cars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', cars_1)
db.commit()
db.close()