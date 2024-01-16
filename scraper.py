import requests
from bs4 import BeautifulSoup
import re
import random

class WebsiteScraper:
    def __init__(self, base_url, search_query_separator, product_container_class, extract_info_functions):
        self.base_url = base_url
        self.search_query_separator = search_query_separator
        self.product_container_class = product_container_class
        self.extract_info_functions = extract_info_functions

    def build_url(self, page, query):
        return self.base_url.format(page=page, query=query)

    def fetch_data(self, url):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        ]
        headers = {"User-Agent": random.choice(user_agents)}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.content 
        else:
            print(f"Received an unexpected status code: {response.status_code}")
            return None

    def parse_html(self, content):
        return BeautifulSoup(content, "html.parser")

    def extract_information(self, soup):
        product_containers = soup.find_all(class_=self.product_container_class)
        products = []
        for product_container in product_containers:
            product_info = self.extract_info_functions(product_container)
            if product_info:
                products.append({
                    'name': product_info['name'],
                    'price': f"{int(re.findall(r'\d+', product_info['price'])[0]):,.0f} грн.",
                    'stock_status': True if product_info['stock_status'] else False
                })
        return products

    def scrape(self, product):
        page = 1
        while True:
            query = product.replace(" ", self.search_query_separator)
            url = self.build_url(page, query)
            content = self.fetch_data(url)

            if not content:
                print(f"No content received from {url}")
                break

            soup = self.parse_html(content)
            print(f"Scraping data from {url}...")

            products_on_page = self.extract_information(soup)
            print(f"Products found on this page: {products_on_page}")

            if not products_on_page:
                print(f"No products found on this page.")
                break

            page += 1

        return products_on_page

websites = [
    WebsiteScraper(
        base_url="https://attack.kiev.ua/search/page-{page}?search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find("h4").find("a").text,
            'price': container.find(class_="price").text.strip(),
            'stock_status': not container.find("button", {"disabled": "disabled"})
        }
    ),

]

product_name = "патч"

for website in websites:
    print(f"\nScraping data from {website.base_url}...\n")
    products = website.scrape(product_name)
    for product in products:
        print(product)
    print("-" * 40)
