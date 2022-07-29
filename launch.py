from logic import BigClass

try:
    page_count = int(input('Enter number of pages'))
except ValueError:
    page_count = 1

if __name__ == "__main__":
    basic = BigClass(''
                     'https://auto.ria.com/uk/search/?indexName=auto&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&',
                     page_count, {
                         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                     })

basic.get_all_cars()
basic.get_all_info()
basic.get_serialized_content()
basic.create_db()
