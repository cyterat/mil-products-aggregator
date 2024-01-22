import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


url = "https://prof1group.ua/search?text=плитоноска"

ua = UserAgent()

headers = {"User-Agent": ua.random}

response = requests.get(url, headers=headers)

print(response.status_code)


soup = BeautifulSoup(response.content, "html.parser")

products_container = soup.find_all(class_="product-card-col")
# print(products_container)

for product in products_container:
    print(type(product))
    print(product.find(class_="product-card__name").text.strip())
    # print(product.find(class_="product-card__price-new js-product-new-price").text.strip())
    # # print(re.search(r"\b\d*", product.find(class_="product-card__price-new js-product-new-price").text.strip()).group(0))
    print(re.search(r"\b\d*", product.find(class_="product-card__price-new js-product-new-price").text.strip()).group(0))
    print(not product.find("span", class_="product-card__label background_not_available"))
    # # print(product.find(class_="product-item-link")["href"])

    # break
    print("\n")