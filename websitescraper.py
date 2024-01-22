import requests
import time
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


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
        self.previous_page_content = set()

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
        # Create an instance of the UserAgent class
        ua = UserAgent()

        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.content
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

    def get_page_content(self, soup):
        """
        Extract relevant content from the page and convert it to a set for comparison.

        Parameters:
        - soup: BeautifulSoup object, the parsed HTML

        Returns:
        - set, the extracted content set
        """
        product_names = [product.text for product in soup.find_all(class_=self.product_container_class)]
        return set(product_names)

    def similarity_check(self, set1, set2):
        """
        Calculate the Jaccard similarity coefficient between two sets.

        Parameters:
        - set1: set, the first set
        - set2: set, the second set

        Returns:
        - float, the Jaccard similarity coefficient
        """
        intersection_size = len(set1.intersection(set2))
        union_size = len(set1.union(set2))
        similarity_coefficient = intersection_size / union_size if union_size != 0 else 0
        return similarity_coefficient

    def detect_duplicate_content(self, current_page_content):
        """
        Compare the content of the current page with the previous page.

        Parameters:
        - current_page_content: set, the content set of the current page

        Returns:
        - bool, indicating whether the content is duplicate
        """
        similarity = self.similarity_check(self.previous_page_content, current_page_content)
        self.previous_page_content = current_page_content
        return similarity >= 0.99  # Adjust the similarity threshold as needed

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
            try:
                product_info = self.extract_info_functions(product_container)

                if product_info is not None and product_info.get('stock_status', False):
                    if 'name' in product_info and 'price' in product_info:
                        product_name = product_info['name'].replace('"', "'")
                        products.append(Product(
                            name=product_name,
                            price=product_info['price'],
                            stock_status=True
                        ))

            except AttributeError:
                pass

            except Exception as e:
                print(f"Error extracting information: {e}")

        if not products:
            print("No products found on this page.")

        print("Finished extraction.")
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

            if not content or content is None:
                print(f"No content received from {url}")
                break

            soup = self.parse_html(content)
            print(f"Scraping data from {url}...")

            current_page_content = self.get_page_content(soup)

            if self.detect_duplicate_content(current_page_content):
                print("Detected duplicate content. Stopping scraping.")
                break

            try:
                products_on_page = self.extract_information(soup)

                if not products_on_page:
                    break

            except Exception as e:
                print(f"Error extracting information: {e}")

            else:
                aggregated_products.extend(products_on_page)

            sleep_duration = random.uniform(1, 3)
            print(f"Sleeping for {sleep_duration:.2f} seconds...\n")
            time.sleep(sleep_duration)

            page += 1

        print(f"Scraped {len(aggregated_products)} products.")
        return aggregated_products
