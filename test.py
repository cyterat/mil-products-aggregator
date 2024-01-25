import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


url = "https://globalballistics.com.ua/ua/all-products/page-4?keyword=сум"

ua = UserAgent()

headers = {"User-Agent": ua.random}

response = requests.get(url, headers=headers)

print(response.status_code)


soup = BeautifulSoup(response.content, "html.parser")

products_container = soup.find_all(class_="product_item")
# print(products_container)
count=0

for product in products_container:
    # Exclude out of stock
    if not product.find(class_="product_preview__button product_preview__button--pre_order fn_is_preorder"):
        print(type(product))
        
        # Name
        print(product.find(class_="product_preview__name_link").text.split("Артикул:")[0].strip())
        
        # Price
        # print(product.find(class_="price").text.strip().replace(" ",""))
        print(product.find(class_="price").find("span",class_="fn_price").text.strip().split(",")[0].replace(" ",""))
        
        # Out of stock
        # print(product.find(class_="status in_stock") != None)
    
    # # # # print(re.search(r"\b\d*", product.find(class_="product-card__price-new js-product-new-price").text.strip()).group(0))
    # print(re.search(r"\b\d{1,3}(?:\s\d{3})*\b", product.find("p", class_="cs-goods-price__value cs-goods-price__value_type_current").text.strip()).group(0).replace(" ",""))
    # print(product.find("p", class_="price_new").text.strip())
    
    count+=1

    # break
    print("\n")

print(count)