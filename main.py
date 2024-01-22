import json
import re
import os
from websitescraper import WebsiteScraper

def aggregate_data(websites, product_name, include_details=True):
    """
    Aggregate data from multiple websites based on a given product.

    Parameters:
    - websites: list of WebsiteScraper objects, websites to scrape data from
    - product_name: str, the product to search for
    - include_details: bool, whether to include details in the output (default is True)

    Returns:
    - list of dictionaries, aggregated data for each website
    """
    aggregated_data = []

    for website in websites:
        print(f"\nScraping data from {website.name}...\n")
        products = website.scrape(product_name)

        if products:
            # Extract relevant information from products
            try:
                prices = [int(product.price) for product in products]
            except ValueError:
                print("Converison of price to integer was unsuccessful. Storing as a string...") 
                prices = [product.price for product in products]
            except Exception as e:
                print("Unexpected error: ", e)
                
            price_uah_min = min(prices)
            price_uah_max = max(prices)
            products_qty = len(products)

            # Create the website's data dictionary without details if include_details is False
            website_data = {
                "website": website.name,
                "price_uah_min": price_uah_min,
                "price_uah_max": price_uah_max,
                "products_qty": products_qty,
                "social_network": website.social_network,
                "tel_vodafone": website.tel_vodafone,
                "tel_kyivstar": website.tel_kyivstar
            }

            # Include details only if include_details is True
            if include_details:
                # Store price as a string if the conversion to integer was unsuccessful
                try:
                    website_data["details"] = [{"product": product.name,"price_uah": int(product.price)} for product in products]
                except ValueError: 
                    website_data["details"] = [{"product": product.name,"price_uah": product.price} for product in products]
                except Exception as e:
                    print("Unexpected error : ", e)
                
            # Append the website's data to the aggregated data list
            aggregated_data.append(website_data)

        print("-" * 40)  # Separator between websites

    return aggregated_data


# List of website instances
websites = [
    # WebsiteScraper(
    #     name="Ataka",
    #     base_url="https://attack.kiev.ua/search/page-{page}?search={query}",
    #     search_query_separator="%20",
    #     product_container_class="product-layout",
    #     extract_info_functions=lambda container: {
    #         'name': container.find("h4").find("a").text,
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip()).group(0).replace(' ',''),
    #         'stock_status': not container.find("button", {"disabled": "disabled"})
    #         },
    #     social_network="https://www.facebook.com/ATAKA.kiev.ua/",
    #     tel_vodafone="+380955587673",
    #     tel_kyivstar="+380679305772"
    #     ),
    # WebsiteScraper(
    #     name="Abrams",
    #     base_url="https://abrams.com.ua/ua/search/?search={query}&page={page}",
    #     search_query_separator="%20",
    #     product_container_class="product-layout",
    #     extract_info_functions=lambda container: {
    #         'name': container.find("h4").find("a").text,
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip()).group(0).replace(' ',''),
    #         'stock_status': "Немає в наявності" not in container.find("div", class_="stock-status").text
    #         },
    #     social_network="https://www.instagram.com/abrams_reserve/",
    #     tel_vodafone="+380955216148",
    #     tel_kyivstar="+380688736587"
    #     ),
    # WebsiteScraper(
    #     name="Hofner",
    #     base_url="https://hofner.com.ua/index.php?route=product/search&search={query}&page={page}",
    #     search_query_separator="%20",
    #     product_container_class="product-layout",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="info_block").find(class_="name").text.strip(),
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_=["price", "price-new"]).text.strip()).group(0).replace(' ',''),
    #         'stock_status': not container.find(class_='outstock_product')
    #         },
    #     social_network="https://www.instagram.com/hofner.ukraine/",
    #     tel_vodafone="",
    #     tel_kyivstar="+380968120013"
    #     ),
    # WebsiteScraper(
    #     name="Ibis",
    #     base_url="https://ibis.net.ua/ua/search/?searchstring={query}&page={page}",
    #     search_query_separator="+",
    #     product_container_class="product_brief_table",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="pb_product_name").text.strip(),
    #         'price': re.search(r"\b\d*", container.find(class_=["pb_price", "pb_price_witholdprice"]).text.strip()).group(0),
    #         'stock_status': not container.find(class_="red")
    #         },
    #     social_network="https://www.instagram.com/ibis_shooting/",
    #     tel_vodafone="",
    #     tel_kyivstar=""
    #     ),
    # WebsiteScraper(
    #     name="Kamber",
    #     base_url="https://kamber.com.ua/katalog/search/filter/page={page}/?q={query}",
    #     search_query_separator="+",
    #     product_container_class="catalog-grid__item",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="catalogCard-title").find("a").text.strip(),
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(' ',''),
    #         'stock_status': not container.find(class_="catalogCard-price __light")
    #         },
    #     social_network="https://www.instagram.com/kamber_tactical/",
    #     tel_vodafone="",
    #     tel_kyivstar="+380684262823"
    #     ),
    # WebsiteScraper(
    #     name="Killa",
    #     base_url="https://killa.com.ua/uk/index.php?route=product/isearch&search={query}&page={page}",
    #     search_query_separator="%20",
    #     product_container_class="product-layout",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="product-thumb").find("h4").find("a").text.strip(),
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip()).group(0).replace(' ',''),
    #         'stock_status': "немає в наявності" not in container.find(class_="caption").find(class_="status").text.lower()
    #         },
    #     social_network="https://www.instagram.com/killa_voentorg",
    #     tel_vodafone="",
    #     tel_kyivstar="+380967980043"
    #     ),
    # WebsiteScraper(
    #     name="Maroder",
    #     base_url="https://maroder.com.ua/uk/page/{page}/?post_type=product&s={query}",
    #     search_query_separator="+",
    #     product_container_class="product-item",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="category-discription-grid").find("h4").find("a").text.strip(),
    #         'price': re.findall(r"\b\d{1,3}(?:,\d{3})*\b", container.find(class_="price").text.strip())[-1].replace(",", ""),
    #         'stock_status': not container.find(class_="out_of_stock_title")
    #         },
    #     social_network="https://www.instagram.com/mrd_tactical/",
    #     tel_vodafone="",
    #     tel_kyivstar="+380685571337"
    #     ),
    # WebsiteScraper(
    #     name="Militarist",
    #     base_url="https://militarist.ua/ua/search/?q={query}&s=&PAGEN_2={page}",
    #     search_query_separator="+",
    #     product_container_class="card_product",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="card_item-name").text.strip(),
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find("p", class_="price_new").text.strip()).group(0).replace(" ",""),
    #         'stock_status': not container.find("div", class_="status no_stock")
    #         },
    #     social_network="http://instagram.com/tm_militarist",
    #     tel_vodafone="",
    #     tel_kyivstar="+380678296207"
    #     ),
    
    # WebsiteScraper(
    #     name="Hitman",
    #     base_url="https://hitman.com.ua/index.php?route=product/search&search={query}&page={page}",
    #     search_query_separator="%20",
    #     product_container_class="product-layout",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="product-name").text.strip(),
    #         'price': container.find(["span", "span"], class_=["price", "price-new"]).text.strip(),
    #         'stock_status': "Не в наявності" not in container.find("div", class_="stock-status").text
    #         },
    #     social_network="https://www.instagram.com/hitman.tactical/",
    #     tel_vodafone="",
    #     tel_kyivstar="+380674784747"
    #     ),
    
    #####################################################################################################
    
    # WebsiteScraper(
    #     name="Militarka",
    #     base_url="https://militarka.com.ua/ua/catalogsearch/result/?q={query}&p={page}",
    #     search_query_separator="+",
    #     product_container_class="product-item-info",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="product-item-name").text.strip(),
    #         'price': re.search(r"\b\d*", container.find(class_="price").text.strip()).group(0),
    #         'stock_status': not container.find(class_="stock unavailable")
    #         },
    #     social_network="https://www.instagram.com/militarka_ua/",
    #     tel_vodafone="+380666163133",
    #     tel_kyivstar="+380673011848"
    #     ),
    # WebsiteScraper(
    #     name="Molli",
    #     base_url="https://molliua.com/katalog/search/filter/page={page}/?q={query}",
    #     search_query_separator="+",
    #     product_container_class="catalog-grid__item",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="catalogCard-title").text.strip(),
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(" ",""),
    #         'stock_status': not container.find(class_="catalogCard-availability __out-of-stock")
    #         },
    #     social_network="https://www.instagram.com/molli.u.a?igshid=NmZiMzY2Mjc%3D",
    #     tel_vodafone="+380994603556",
    #     tel_kyivstar="+380962019665"
    #     ),   
    # WebsiteScraper(
    #     name="Prof1Group",
    #     base_url="https://prof1group.ua/search?text={query}&page={page}",
    #     search_query_separator="+",
    #     product_container_class="product-card-col",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="product-card__name").text.strip(),
    #         'price': re.search(r"\b\d*", container.find(class_="product-card__price-new js-product-new-price").text.strip()).group(0),
    #         'stock_status': not container.find("span", class_="product-card__label background_not_available")
    #         },
    #     social_network="https://www.instagram.com/prof1group.ua/",
    #     tel_vodafone="",
    #     tel_kyivstar="+380676595979"
    #     ),   
    # WebsiteScraper(
    #     name="Punisher",
    #     base_url="https://punisher.com.ua/magazin/search/filter/page={page}/?q={query}",
    #     search_query_separator="+",
    #     product_container_class="catalog-grid__item",
    #     extract_info_functions=lambda container: {
    #         'name': container.find(class_="catalogCard-title").text.strip(),
    #         'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(" ",""),
    #         'stock_status': container.find(class_="btn __special j-buy-button-add") != None
    #         },
    #     social_network="https://www.instagram.com/punisher.com.ua/",
    #     tel_vodafone="+380500587070",
    #     tel_kyivstar="+380970587000"
    #     ), 
    
    ]


# Dummy product name
product_name = "плитоноска"

# Replace multiple consecutive whitespaces with a single one
fmt_product_name = re.sub(r'\s+', ' ', product_name).lower()
    
# Aggregate data and write to JSON file
result = aggregate_data(websites, fmt_product_name, include_details=True)

# Sorting the list of dictionaries based on 'price_uah_min'
sorted_result = sorted(result, key=lambda x: x['price_uah_min'], reverse=False)  # Set reverse=True for descending order

# Sorting the 'details' list within each dictionary based on 'price_uah'
for entry in sorted_result:
    entry['details'] = sorted(entry['details'], key=lambda x: x['price_uah'], reverse=False)  # Set reverse=True for descending order

# Create path
output_file_path = os.path.join(os.getcwd(),"data","output.json")

# Write to JSON file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(sorted_result, output_file, indent=2, ensure_ascii=False)

print(f"Data written to {output_file_path}")
