import re
from datetime import datetime
from bs4 import BeautifulSoup

car_list = []
cars_1 = []


def serialize(content, data, url):
    name_model_year = str(content.find('h1', class_="head").text).split(' ')
    probeg = content.find('div', class_="technical-info", id="details").find('dd', class_="mhide").find(
        'span', class_="argument").text
    city = content.find('div', class_="item_inner").text
    tech_info = content.find('div', class_="technical-info", id="details").text
    tech_info = tech_info.replace('•', ' ').split(' ')
    tech_info = str.join(' ', tech_info)
    try:
        probeg_per_year = int(probeg.split(' ')[0]) / (int(datetime.now().year) - int(name_model_year[-1]))
    except ZeroDivisionError:
        probeg_per_year = int(probeg.split(' ')[0]) / 1
    try:
        objem = re.search(r'\d[.]\d\d?\sл\s? | \d\sл\s?', str(tech_info)).group(0)
    except AttributeError:
        objem = re.search(r'\d[.]\d\d?\sл\s? | \d\sл\s?', str(tech_info))
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
    try:
        price_uah = int(str.join('', price_usd.replace('$', '').split())) * 40.56
    except ValueError:
        price_uah = price_usd
    current_car = {
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
        "price_uah": price_uah,
        "url": url
    }
    car_list.append(current_car)


def serialize_(car_list):
    for car in car_list:
        tuple_ = tuple(car.values())
        cars_1.append(tuple_)
