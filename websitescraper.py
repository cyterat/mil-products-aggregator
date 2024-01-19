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


    def extract_information(self, soup):
        """
        Extracts product information from the parsed HTML.

        Parameters:
        - soup: BeautifulSoup object, the parsed HTML

        Returns:
        - list of Product objects, the extracted product information
        """
        # Find all HTML elements with the specified product container class
        product_containers = soup.find_all(class_=self.product_container_class)
        products = []

        # Iterate through each product container
        for product_container in product_containers:
            try:
                # Extract product information using the specified extraction functions
                product_info = self.extract_info_functions(product_container)
                
                # Check if product_info is not None and the product is in stock
                if product_info is not None and product_info.get('stock_status', False):
                    # Check if 'name' and 'price' are present in product_info
                    if 'name' in product_info and 'price' in product_info:
                        # Replace double quotes with single quotes in the product name
                        product_name = product_info['name'].replace('"', "'")

                        # Append a Product object to the list of products
                        products.append(Product(
                            name=product_name,
                            # price=int(product_info['price']),
                            price=product_info['price'],
                            stock_status=True
                        ))

            except AttributeError:
                # Ignore error related to scraping empty pages on some websites
                pass
            
            except Exception as e:
                # Display other errors
                print(f"Error extracting information: {e}")

        # Print a message if no products were found on the page
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
        # Initialize variables
        page = 1
        aggregated_products = []

        # Infinite loop to iterate over pages
        while True:
            # Format the product name for the URL query
            query = product.replace(" ", self.search_query_separator)
            
            # Build the URL for the current page and query
            url = self.build_url(page, query)
            
            # Fetch HTML content from the URL
            content = self.fetch_data(url)

            # Check if content is empty or None
            if not content or content is None:
                print(f"No content received from {url}")
                break

            # Parse HTML content using BeautifulSoup
            soup = self.parse_html(content)
            print(f"Scraping data from {url}...")

            try:
                # Extract product information from the parsed HTML
                products_on_page = self.extract_information(soup)
                
                # Check if no products were found on the current page
                if not products_on_page:
                    break

            except Exception as e:
                # Handle any errors that occur during information extraction
                print(f"Error extracting information: {e}")

            else:
                # Extend the list of aggregated products with products from the current page
                aggregated_products.extend(products_on_page)

            # Add a random sleep between 1 and 3 seconds to simulate human-like behavior
            sleep_duration = random.uniform(1, 3)
            print(f"Sleeping for {sleep_duration:.2f} seconds...\n")
            time.sleep(sleep_duration)

            # Move to the next page
            page += 1

        # Print the total number of products scraped
        print(f"Scraped {len(aggregated_products)} products.")
        return aggregated_products
