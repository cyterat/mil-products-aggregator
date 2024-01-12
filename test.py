import requests
import re
from bs4 import BeautifulSoup

website = "https://ibis.net.ua" 
search_url = "https://ibis.net.ua/ua/search/?searchstring="

# product = input("Enter a product to search: ")
product = "AR"

search_query = product.replace(" ", "+")

full_url = search_url + search_query
print(full_url)

response = requests.get(full_url)

soup = BeautifulSoup(response.content, "html.parser")

products = soup.find_all(class_="pb_product_name")
prices = soup.find_all(class_="pb_price")

number_found_products = soup.find_all(class_="category_name center")
number_found_products = int(re.findall(r"\d+", number_found_products[0].text)[0])
print(f"\nFound {number_found_products:,.0f} items.\n")

price_list = []
for prod, price in zip(products, prices):
    print(prod.text, "---", f"{int(re.findall(r"\d+", price.text)[0]):,.0f} грн.")
    print(website + prod["href"], "\n")
    price_list.append(int(re.findall(r"\d+", price.text)[0]))

min_price = f"{min(price_list):,.0f}"
max_price = f"{max(price_list):,.0f}"

print("Price range: ", min_price, "-", max_price, "грн.")
