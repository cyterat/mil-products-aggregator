import requests
from bs4 import BeautifulSoup
import re
import time
import random

class WebsiteScraper:
    def __init__(self, base_url, search_query_separator, product_container_class, extract_info_functions):
        # Initialize the scraper with essential information
        self.base_url = base_url
        self.search_query_separator = search_query_separator
        self.product_container_class = product_container_class
        self.extract_info_functions = extract_info_functions

    def build_url(self, page, query):
        # Build the complete URL with placeholders replaced
        return self.base_url.format(page=page, query=query)

    def fetch_data(self, url):
        # Send a GET request to the specified URL with a random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.56 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko"
        ]
        headers = {"User-Agent": random.choice(user_agents)}
        response = requests.get(url, headers=headers)

        # Handle different HTTP status codes
        if response.status_code == 200:
            return response.content
        elif response.status_code == 403:
            print(f"Received a 403 error. Retrying after a delay.")
            time.sleep(random.uniform(5, 10))  # Add a random delay between 5 and 10 seconds
            return self.fetch_data(url)  # Retry the request
        else:
            print(f"Received an unexpected status code: {response.status_code}")
            return None

    def parse_html(self, content):
        # Parse the HTML content using BeautifulSoup
        return BeautifulSoup(content, "html.parser")

    def extract_information(self, soup):
        # Extract product information from the parsed HTML
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
        # Main scraping function that iterates over pages and extracts information
        page = 1
        while True:
            query = product.replace(" ", self.search_query_separator)
            url = self.build_url(page, query)
            content = self.fetch_data(url)

            # Check if content was received
            if not content:
                print(f"No content received from {url}")
                break

            soup = self.parse_html(content)
            print(f"Scraping data from {url}...")

            products_on_page = self.extract_information(soup)
            print(f"Products found on this page: {products_on_page}")

            # Check if there are no products on this page
            if not products_on_page:
                print(f"No products found on this page.")
                break

            # Move to the next page
            page += 1

        return products_on_page