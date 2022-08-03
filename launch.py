from logic import Parser

try:
    page_count = int(input('Enter number of pages \n'))
except ValueError:
    page_count = 1

url = 'https://auto.ria.com/uk/search/?indexName=auto&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&'
header = {
         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }

Parser(url, page_count, header).start()