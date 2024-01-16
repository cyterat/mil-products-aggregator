import requests
import re
import os
import sys
import time
import random

from bs4 import BeautifulSoup
import pandas as pd
pd.options.display.max_colwidth=None


excel_dir = os.path.join("data", "buy-mil-equipment.xlsx")

# Read websites data from an Excel file
websites_df = (
    pd.read_excel(
        excel_dir,
        sheet_name="main",
        skiprows=7, 
        usecols=[
            "name",
            "url_base",
            "url_headers_placeholders",
            "search_query_separator"
            ],
        converters={
            "name": lambda x: str(x).strip(),
            "url_base": lambda x: str(x).strip(),
            "url_headers_placeholders": lambda x: str(x).strip(),
            "search_query_separator": lambda x: str(x).strip()
            }
        )
    .dropna()
    .replace("NONE", "")   # replace 'NONE' placeholder with empty string
    .reset_index(drop=True)
    )

# New column with concatenated base URL and the headers with placeholders
websites_df = websites_df.assign(full_url_placeholders = websites_df["url_base"] + websites_df["url_headers_placeholders"])

# print(websites_df)

#                   name                         url_base                                     url_headers_placeholders search_query_separator                                                                 full_url_placeholders
# 0                Ataka           https://attack.kiev.ua                           /search/page-{page}?search={query}                    %20                              https://attack.kiev.ua/search/page-{page}?search={query}
# 1               Abrams            https://abrams.com.ua                       /ua/search/?search={query}&page={page}                    %20                           https://abrams.com.ua/ua/search/?search={query}&page={page}
# 2               Hitman            https://hitman.com.ua                       /ua/search/?search={query}&page={page}                    %20                           https://hitman.com.ua/ua/search/?search={query}&page={page}
# 3               Hofner            https://hofner.com.ua   /index.php?route=product/search&search={query}&page={page}                    %20       https://hofner.com.ua/index.php?route=product/search&search={query}&page={page}
# 4                 Ibis              https://ibis.net.ua                 /ua/search/?searchstring={query}&page={page}                      +                       https://ibis.net.ua/ua/search/?searchstring={query}&page={page}
# ...

##########################################################################
##########################################################################

# TEMPORARY STATIC product to search for. This must be replaced with an input statement to allow the user to enter the product name
product = "патч"
# product = input("Enter a product to search: ")

# Configure the session and set user-agent header
session = requests.Session()

# List of user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.56 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko"
]

for i, raw_url in enumerate(websites_df["full_url_placeholders"]):
    # TEMPORARY static page value
    page = 1
    print(websites_df.loc[i,"name"])
    # while True:
    while i < 2:
        # Assign separator between words to a variable 
        query = product.replace(" ", websites_df.loc[i, "search_query_separator"])
        
        # Substitute placeholders on the current page URL
        if "strikeshop" in raw_url:  # first page on this website is written as 'p-0' in the URL
            url = raw_url.format(page=page-1, query=query)
        else:
            url = raw_url.format(page=page, query=query)
            
        # Randomly select a user agent
        user_agent = random.choice(user_agents)
        
        # Set the user-agent header
        headers = {"User-Agent": user_agent}
        
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        
        # Check if the page exists
        if response.status_code == 200:
            # Parse the content of the response with BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all product containers on the page
            product_containers = soup.find_all(class_="product-layout")

            # Check if there are no product containers on the page
            if not product_containers:
                break

            # Iterate through the product containers and print names and prices for available products
            for product_container in product_containers:
                product_name = product_container.find("h4").find("a").text
                price = product_container.find(class_="price").text.strip()
                availability_button = product_container.find("button", {"disabled": "disabled"})

                if not availability_button:
                    print()
                    print("Product Name:", product_name)
                    print("Price:", f"{int(re.findall(r'\d+', price)[0]):,.0f} грн.")
                    print("Availability: Available")
                    print()
                
            # Wait for a random sleep interval (1 to 3 seconds)
            time.sleep(random.uniform(1, 3))
            
            # Move to the next page
            page += 1
        else:
            # If the page doesn't exist, break the loop
            break


sys.exit()

##########################################################################
##########################################################################

# Send a GET request to the website
response = requests.get(full_url)

# Parse the content of the response with BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find all product names and prices on the page
products = soup.find_all(class_="pb_product_name")
prices = soup.find_all(class_="pb_price")

# Find the total number of products found and convert it to an integer
number_found_products = soup.find_all(class_="category_name center")
number_found_products = int(re.findall(r'\d+', number_found_products[0].text)[0])
print(f"\nFound {number_found_products:,.0f} items.\n")

# Initialize a list to store the prices
price_list = []

# Loop through each product and price, print them, and add the price to the price list
for prod, price in zip(products, prices):
    print(prod.text, "---", f"{int(re.findall(r'\d+', price.text)[0]):,.0f} грн.")
    print(base_url + prod["href"], "\n")
    price_list.append(int(re.findall(r'\d+', price.text)[0]))

# Find the minimum and maximum price in the price list
min_price = f"{min(price_list):,.0f}"
max_price = f"{max(price_list):,.0f}"

# Print the price range
print("Price range: ", min_price, "-", max_price, "грн.")
