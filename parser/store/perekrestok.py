import json
import time
from requests import Session
import urllib.parse

from db.pw_model import Product
from store.stocks_info import Stock


# whitelist_id = [113, 148, 100, 708, 187, 205, 242,
#                 132, 782, 174, 54, 793, 217, 79, 224, 168, 74, 1]


class PerekrestokParser:

    store_id = 3
    store_code = 'perekrestok'

    def __init__(self, stock: Stock) -> None:
        self.stock = stock
        self.client = Session()
        self.client.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Linux; U; Linux i674 ) Gecko/20130401 Firefox/62.8'})
        self.init()
        self.set_stock()

    def init(self):
        self.client.get('https://www.perekrestok.ru/')
        cookies = self.client.cookies.get_dict()
        session_data = urllib.parse.unquote(cookies['session'])
        self.client.headers['Auth'] = f'Bearer {
            json.loads(session_data)['accessToken']}'

    def set_stock(self):
        r = self.client.put(
            f'https://www.perekrestok.ru/api/customer/1.4.1.0/delivery/mode/pickup/{self.stock.stock_id}')
        r.raise_for_status()

    def fetch_categories(self):
        r = self.client.get('https://www.perekrestok.ru/api/customer/1.4.1.0/catalog')

        categories = []

        for ctg in r.json()['content']['categories']:
            category = {'id': ctg['category']['id'], 
                        'name': ctg['category']['title'], 
                        'code': ctg['category']['slug'], 
                        'children': []
                        }
            for subctg in ctg['children']:
                subcategory = {'id': ctg['category']['id'], 
                               'name': subctg['category']['title'], 
                               'code': subctg['category']['slug']
                                }
                category['children'].append(subcategory)

            categories.append(category)

        return categories

    def fetch_products(self, category_id, v=False, sleep_sec=1):
        page = 1
        per_page = 100
        next_page_exists = True
        products = []
        total_parsed = 0

        url = 'https://www.perekrestok.ru/api/customer/1.4.1.0/catalog/product/feed'
        while next_page_exists:
            r = self.client.post(url, json={"page": page, "perPage": per_page, "filter": {
                "category": category_id, "onlyWithProductReviews": False}, "withBestProductReviews": False},)
            data = r.json()['content']
            next_page_exists = data['paginator']['nextPageExists']
            total_parsed += len(data['items'])

            if v:
                print('url', url, total_parsed)

            for p in data['items']:
                products.append(
                    {'id': p['id'], 
                     'name': p['title'], 
                     'code': p['masterData']['slug'], 
                     'price': p['priceTag']['price']/100
                    })

            page += 1
            time.sleep(sleep_sec)

        return products

    def start(self) -> list[Product]:
        ctgs = self.fetch_categories()

        all_products = []

        for ctg in ctgs:
            time.sleep(1)
            print(PerekrestokParser.store_code, self.stock.region, ctg['name'])
            products = self.fetch_products(
                category_id=ctg['id'], v=False, sleep_sec=0.2)
            data = [Product(product_id=f'{PerekrestokParser.store_code}-{p['id']}',
                            store_id=PerekrestokParser.store_id,
                            region_id=self.stock.region_id,
                            name=p['name'],
                            code=p['code'],
                            category=ctg['name'],
                            category_code=ctg['code'],
                            price=p['price']) for p in products
                    ]
            all_products += data

        return all_products
