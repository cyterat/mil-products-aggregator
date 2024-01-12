import requests
import re
import os
import sys

from bs4 import BeautifulSoup
import pandas as pd
pd.options.display.max_colwidth=None


excel_dir = os.path.join("data", "buy-mil-equipment.xlsx")

websites_df = (
    pd.read_excel(
        excel_dir,
        skiprows=3, 
        usecols=["name","website_url","search_request_format","search_request_base","separator"],
        converters={
            "name": lambda x: str(x).strip(),
            "website_url": lambda x: str(x).strip(),
            "search_request_format": lambda x: str(x).strip(),
            "search_request_base": lambda x: str(x).strip(),
            "separator": lambda x: str(x).strip()
            }
        )
    .dropna()
    .reset_index(drop=True)
    )

print(websites_df)
#              name                    website_url                                                          search_request_format                                                search_request_base separator
# 0           Ataka         https://attack.kiev.ua                             https://attack.kiev.ua/search/?search=шарф%20труба                             https://attack.kiev.ua/search/?search=       %20
# 1          Abrams          https://abrams.com.ua                           https://abrams.com.ua/ua/search/?search=шарф%20труба                           https://abrams.com.ua/ua/search/?search=       %20
# 2          Hitman       https://hitman.com.ua/ua       https://hitman.com.ua/index.php?route=product/search&search=шарф%20труба       https://hitman.com.ua/index.php?route=product/search&search=       %20
# 3          Hofner          https://hofner.com.ua       https://hofner.com.ua/index.php?route=product/search&search=шарф%20труба       https://hofner.com.ua/index.php?route=product/search&search=       %20
# 4            Ibis            https://ibis.net.ua                         https://ibis.net.ua/ua/search/?searchstring=шарф+труба                       https://ibis.net.ua/ua/search/?searchstring=         +
# ...

sys.exit()


# Define the base URL and search URL of the website
base_url = "https://ibis.net.ua" 
search_url = "https://ibis.net.ua/ua/search/?searchstring="

# Define the product to search for. This can be replaced with an input statement to allow the user to enter the product name
product = "Opinel"
# product = input("Enter a product to search: ")

# Replace spaces in the product name with '+' to format it for the search URL
search_query = product.replace(" ", "+")

# Combine the search URL and the formatted product name to create the full URL
full_url = search_url + search_query
print("\n", full_url)

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
