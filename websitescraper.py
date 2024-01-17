import requests
from bs4 import BeautifulSoup
import re
import time
import random

class Product:
    def __init__(self, name, price, stock_status):
        """
        Represents a product with its name, price, and stock status.

        Parameters:
        - name: str, the name of the product
        - price: str, the price of the product
        - stock_status: bool, the availability status of the product
        """
        self.name = name
        self.price = price
        self.stock_status = stock_status

class WebsiteScraper:
    def __init__(self, name, base_url, search_query_separator, product_container_class, extract_info_functions, social_network, tel_vodafone, tel_kyivstar):
        """
        Represents a website scraper with specific parameters.

        Parameters:
        - name: str, the name of the website
        - base_url: str, the base URL template for scraping
        - search_query_separator: str, separator for search queries in the URL
        - product_container_class: str, class name of the HTML container for product information
        - extract_info_functions: function, function to extract information from a product container
        - social_network: str, the social network associated with the website
        - tel_vodafone: str, Vodafone contact number for the website
        - tel_kyivstar: str, Kyivstar contact number for the website
        """
        self.name = name
        self.base_url = base_url
        self.search_query_separator = search_query_separator
        self.product_container_class = product_container_class
        self.extract_info_functions = extract_info_functions
        self.social_network = social_network
        self.tel_vodafone = tel_vodafone
        self.tel_kyivstar = tel_kyivstar

    def build_url(self, page, query):
        """
        Build the complete URL with placeholders replaced.

        Parameters:
        - page: int, the page number
        - query: str, the search query

        Returns:
        - str, the constructed URL
        """
        return self.base_url.format(page=page, query=query)

    def fetch_data(self, url):
        """
        Send a GET request to the specified URL with a random user agent.

        Parameters:
        - url: str, the URL to send the GET request to

        Returns:
        - bytes, the content of the response or None if an error occurs
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.56 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko"
        ]
        headers = {"User-Agent": random.choice(user_agents)}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.content
        elif response.status_code == 403:
            print(f"Received a 403 error. Retrying after a delay.")
            time.sleep(random.uniform(5, 10))
            return self.fetch_data(url)
        else:
            print(f"Received an unexpected status code: {response.status_code}")
            return None

    def parse_html(self, content):
        """
        Parse the HTML content using BeautifulSoup.

        Parameters:
        - content: bytes, the HTML content to parse

        Returns:
        - BeautifulSoup object, the parsed HTML
        """
        return BeautifulSoup(content, "html.parser")

    def extract_information(self, soup):
        """
        Extract product information from the parsed HTML.

        Parameters:
        - soup: BeautifulSoup object, the parsed HTML

        Returns:
        - list of Product objects, the extracted product information
        """
        product_containers = soup.find_all(class_=self.product_container_class)
        products = []
        for product_container in product_containers:
            product_info = self.extract_info_functions(product_container)
            if product_info and product_info['stock_status']:
                # Replace double quotes with single quotes in the product name
                product_name = product_info['name'].replace('"', "'")
                products.append(Product(
                    name=product_name,
                    price=f"{int(re.findall(r'\d+', product_info['price'])[0]):,.0f} грн.",
                    stock_status=True
                ))
        return products

    def scrape(self, product):
        """
        Main scraping function that iterates over pages and extracts information.

        Parameters:
        - product: str, the product to search for

        Returns:
        - list of Product objects, the aggregated product information
        """
        page = 1
        aggregated_products = []
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

            if not products_on_page:
                print(f"No products found on this page.")
                break

            aggregated_products.extend(products_on_page)
            
            # Add a random sleep between 1 and 3 seconds
            sleep_duration = random.uniform(1, 3)
            print(f"Sleeping for {sleep_duration:.2f} seconds...")
            time.sleep(sleep_duration)
            
            page += 1

        return aggregated_products
