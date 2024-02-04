import json
import re
import os
import time
import asyncio
import logging
import argparse
from websitescraper import WebsiteScraper


# Create logs path
log_file_path = os.path.join('logs', 'main.log')

# Set up logging
logging.basicConfig(filename=log_file_path, level=logging.INFO, encoding='utf-8', filemode='w')


async def async_scrape(website, product_name):
    # print(f"Scraping data from {website.name}...")
    products = await asyncio.to_thread(website.scrape, product_name)
    return website, products


async def aggregate_data(websites, product_name, include_details=True):
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

    # Create a list of coroutines for asynchronous execution
    tasks = [async_scrape(website, product_name) for website in websites]

    # Gather and wait for results
    results = await asyncio.gather(*tasks)

    for website, products in results:
        if products:
            # Extract relevant information from products
            try:
                prices = [int(product.price) for product in products]
            except ValueError:
                logging.warning("Conversion of price to integer was unsuccessful. Storing as a string...")
                prices = [product.price for product in products]
            except Exception as e:
                logging.error("Unexpected error: ", e)

            price_uah_min = min(prices)
            price_uah_max = max(prices)
            products_qty = len(products)

            # Create the website's data dictionary without details if include_details is False
            website_data = {
                "website": website.name,
                "search_query_url": website.generate_search_query_url(product_name).replace(" ", website.search_query_separator),
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
                    website_data["details"] = [{"product": product.name, "price_uah": int(product.price)} for product in products]
                except ValueError:
                    website_data["details"] = [{"product": product.name, "price_uah": product.price} for product in products]
                except Exception as e:
                    logging.error("Unexpected error : ", e)

            # Append the website's data to the aggregated data list
            aggregated_data.append(website_data)

    return aggregated_data


def export_to_json(sorted_result):
    """This function writes script output into
    a JSON file

    Args:
        sorted_result (list): list of dictionaries
    """
    # Create path
    output_file_path = os.path.join(os.getcwd(),"data","output.json")

    # Write to JSON file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(sorted_result, output_file, indent=2, ensure_ascii=False)

    print(f"\nData written to {output_file_path}")
    

def display_scraped_data(sorted_result):
    """This function displays scraped data

    Args:
        sorted_result (list): list of dictionaries
    """
    # Store total number of matching products on each website
    total_products_qty = sum([website["products_qty"] for website in sorted_result])
    print("\nЗнайдено товарів:", total_products_qty)
    print("")

    for website in sorted_result:
        # Online store name
        print(f"<b>{website['website']}</b>")
        # Number of found products
        print("◽", f"К-сть: {website["products_qty"]} шт.")
        
        # Display single price when max and min prices are the same
        if website["price_uah_min"] == website["price_uah_max"]:
            print("◽", f"Ціна: {website["price_uah_min"]:,} грн.")
        else:
            print("◽", f"Ціна: {website["price_uah_min"]:,} -- {website["price_uah_max"]:,} грн.")
        
        # Products page link
        print(f"<a href='{website['search_query_url']}'>перейти→</a>")
        
        print("")


# Start the timer
start_time = time.time()

# List of website instances
websites = [
    WebsiteScraper(
        name="Ataka",
        base_url="https://attack.kiev.ua/search/page-{page}?search={query}",
        search_query_url="https://attack.kiev.ua/search?search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find("h4").find("a").text,
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip()).group(0).replace(' ',''),
            'stock_status': not container.find("button", {"disabled": "disabled"})
            },
        social_network="https://www.facebook.com/ATAKA.kiev.ua/",
        tel_vodafone="+380955587673",
        tel_kyivstar="+380679305772"
        ),
    WebsiteScraper(
        name="Abrams",
        base_url="https://abrams.com.ua/ua/search/?search={query}&page={page}",
        search_query_url="https://abrams.com.ua/ua/search/?search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find("h4").find("a").text,
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip()).group(0).replace(' ',''),
            'stock_status': "Немає в наявності" not in container.find("div", class_="stock-status").text
            },
        social_network="https://www.instagram.com/abrams_reserve/",
        tel_vodafone="+380955216148",
        tel_kyivstar="+380688736587"
        ),
    WebsiteScraper(
        name="Hofner",
        base_url="https://hofner.com.ua/index.php?route=product/search&search={query}&page={page}",
        search_query_url="https://hofner.com.ua/index.php?route=product/search&search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find(class_="info_block").find(class_="name").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_=["price", "price-new"]).text.strip()).group(0).replace(' ',''),
            'stock_status': not container.find(class_='outstock_product')
            },
        social_network="https://www.instagram.com/hofner.ukraine/",
        tel_vodafone="",
        tel_kyivstar="+380968120013"
        ),
    WebsiteScraper(
        name="Ibis",
        base_url="https://ibis.net.ua/ua/search/?searchstring={query}&page={page}",
        search_query_url="https://ibis.net.ua/ua/search/?searchstring={query}",
        search_query_separator="+",
        product_container_class="product_brief_table",
        extract_info_functions=lambda container: {
            'name': container.find(class_="pb_product_name").text.strip(),
            'price': re.search(r"\b\d*", container.find(class_=["pb_price", "pb_price_witholdprice"]).text.strip()).group(0),
            'stock_status': not container.find(class_="red")
            },
        social_network="https://www.instagram.com/ibis_shooting/",
        tel_vodafone="",
        tel_kyivstar=""
        ),
    WebsiteScraper(
        name="Kamber",
        base_url="https://kamber.com.ua/katalog/search/filter/page={page}/?q={query}",
        search_query_url="https://kamber.com.ua/katalog/search/filter/?q={query}",
        search_query_separator="+",
        product_container_class="catalog-grid__item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="catalogCard-title").find("a").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(' ',''),
            'stock_status': not container.find(class_="catalogCard-price __light")
            },
        social_network="https://www.instagram.com/kamber_tactical/",
        tel_vodafone="",
        tel_kyivstar="+380684262823"
        ),
    # WebsiteScraper(
    #     name="Killa",
    #     base_url="https://killa.com.ua/uk/index.php?route=product/isearch&search={query}&page={page}",
    #     search_query_url="https://killa.com.ua/uk/index.php?route=product/isearch&search={query}",
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
    WebsiteScraper(
        name="Maroder",
        base_url="https://maroder.com.ua/uk/page/{page}/?post_type=product&s={query}",
        search_query_url="https://maroder.com.ua/uk/?post_type=product&s={query}",
        search_query_separator="+",
        product_container_class="product-item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="category-discription-grid").find("h4").find("a").text.strip(),
            'price': re.findall(r"\b\d{1,3}(?:,\d{3})*\b", container.find(class_="price").text.strip())[-1].replace(",", ""),
            'stock_status': not container.find(class_="out_of_stock_title")
            },
        social_network="https://www.instagram.com/mrd_tactical/",
        tel_vodafone="",
        tel_kyivstar="+380685571337"
        ),
    WebsiteScraper(
        name="Militarist",
        base_url="https://militarist.ua/ua/search/?q={query}&s=&PAGEN_2={page}",
        search_query_url="https://militarist.ua/ua/search/?q={query}",
        search_query_separator="+",
        product_container_class="card_product",
        extract_info_functions=lambda container: {
            'name': container.find(class_="card_item-name").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find("p", class_="price_new").text.strip()).group(0).replace(" ",""),
            'stock_status': not container.find("div", class_="status no_stock")
            },
        social_network="http://instagram.com/tm_militarist",
        tel_vodafone="",
        tel_kyivstar="+380678296207"
        ),
    WebsiteScraper(
        name="Militarka",
        base_url="https://militarka.com.ua/ua/catalogsearch/result/?q={query}&p={page}",
        search_query_url="https://militarka.com.ua/ua/catalogsearch/result/?q={query}",
        search_query_separator="+",
        product_container_class="product-item-info",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product-item-name").text.strip(),
            'price': re.search(r"\b\d*", container.find(class_="price").text.strip()).group(0),
            'stock_status': not container.find(class_="stock unavailable")
            },
        social_network="https://www.instagram.com/militarka_ua/",
        tel_vodafone="+380666163133",
        tel_kyivstar="+380673011848"
        ),
    WebsiteScraper(
        name="Molli",
        base_url="https://molliua.com/katalog/search/filter/page={page}/?q={query}",
        search_query_url="https://molliua.com/katalog/search/filter/?q={query}",
        search_query_separator="+",
        product_container_class="catalog-grid__item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="catalogCard-title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(" ",""),
            'stock_status': not container.find(class_="catalogCard-availability __out-of-stock")
            },
        social_network="https://www.instagram.com/molli.u.a?igshid=NmZiMzY2Mjc%3D",
        tel_vodafone="+380994603556",
        tel_kyivstar="+380962019665"
        ),   
    WebsiteScraper(
        name="Prof1Group",
        base_url="https://prof1group.ua/search?text={query}&page={page}",
        search_query_url="https://prof1group.ua/search?text={query}",
        search_query_separator="+",
        product_container_class="product-card-col",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product-card__name").text.strip(),
            'price': re.search(r"\b\d*", container.find(class_="product-card__price-new js-product-new-price").text.strip()).group(0),
            'stock_status': not container.find("span", class_="product-card__label background_not_available")
            },
        social_network="https://www.instagram.com/prof1group.ua/",
        tel_vodafone="",
        tel_kyivstar="+380676595979"
        ),   
    WebsiteScraper(
        name="Punisher",
        base_url="https://punisher.com.ua/magazin/search/filter/page={page}/?q={query}",
        search_query_url="https://punisher.com.ua/magazin/search/filter/?q={query}",
        search_query_separator="+",
        product_container_class="catalog-grid__item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="catalogCard-title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(" ",""),
            'stock_status': container.find(class_="btn __special j-buy-button-add") != None
            },
        social_network="https://www.instagram.com/punisher.com.ua/",
        tel_vodafone="+380500587070",
        tel_kyivstar="+380970587000"
        ), 
    WebsiteScraper(
        name="Specprom-kr",
        base_url="https://specprom-kr.com.ua/index.php?route=product/search&search={query}&page={page}",
        search_query_url="https://specprom-kr.com.ua/index.php?route=product/search&search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product-name").text.strip(),
            'price': container.find_all(class_=["special_no_format","price_no_format"])[-1].text.split(".")[0].replace(" ",""),
            'stock_status': not container.find(class_="stock-status outofstock")
            },
        social_network="https://www.instagram.com/specprom_kr/",
        tel_vodafone="",
        tel_kyivstar=""
        ), 
    WebsiteScraper(
        name="Sts",
        base_url="https://sts-gear.com/ua/site_search/page_{page}?search_term={query}",
        search_query_url="https://sts-gear.com/ua/site_search/?search_term={query}",
        search_query_separator="+",
        product_container_class="cs-online-edit cs-product-gallery__item js-productad",
        extract_info_functions=lambda container: {
            'name': container.find(class_="cs-goods-title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="cs-goods-price__value cs-goods-price__value_type_current").text).group(0).replace(" ",""),
            'stock_status': "Немає в наявності" not in container.find(attrs={"data-qaid":"presence_data"})
            },
        social_network="https://www.instagram.com/stsgear/",
        tel_vodafone="",
        tel_kyivstar="+38674457255"
        ), 
    WebsiteScraper(
        name="Sturm",
        base_url="https://sturm.com.ua/search/?search={query}&page={page}",
        search_query_url="https://sturm.com.ua/search/?search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find(class_="caption").find("h4").text.strip(),
            'price': re.search(r"\b\d*",  container.find(class_="price-new").text.replace(" ","")).group(0),
            'stock_status': "Закінчився" not in container.find("button", class_="button-cart")
            },
        social_network="https://www.facebook.com/sturmmag/",
        tel_vodafone="+380667590005",
        tel_kyivstar="+380671723639"
        ), 
    WebsiteScraper(
        name="Stvol",
        base_url="https://stvol.ua/search?page={page}&query={query}",
        search_query_url="https://stvol.ua/search?query={query}",
        search_query_separator="+",
        product_container_class="product-card product-card--theme-catalog",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product-card__title").text.strip(),
            'price': container.find(class_="product-card__price product-card__price--current").text.strip().split(".")[0].replace(" ",""),
            'stock_status': "Товар закінчився" not in container.find(class_="product-card__bottom")
            },
        social_network="https://www.instagram.com/stvol_ua/",
        tel_vodafone="+380504177677",
        tel_kyivstar=""
        ), 
    WebsiteScraper(
        name="Tactical Gear",
        base_url="https://tacticalgear.ua/products?keyword={query}&page={page}",
        search_query_url="https://tacticalgear.ua/products?keyword={query}",
        search_query_separator="+",
        product_container_class="item product sku b1c-good",
        extract_info_functions=lambda container: {
            'name': container.find(class_="name").text.strip(),
            'price': container.find(class_="price").text.strip().split("грн")[0].replace(" ","").split(".")[0].replace(" ",""),
            'stock_status': "Точно є у наявності!" in container.find(class_="inStock label changeAvailable")
            },
        social_network="https://www.instagram.com/tacticalgear.ua/",
        tel_vodafone="+380959010002",
        tel_kyivstar="+380979010002"
        ), 
    WebsiteScraper(
        name="Ukr Armor",
        base_url="https://ukrarmor.com.ua/search?page={page}&search={query}",
        search_query_url="https://ukrarmor.com.ua/search?search={query}",
        search_query_separator="+",
        product_container_class="product-card product-card--default",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product-card__title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="product-card__price--current").text.strip()).group(0).replace(" ",""),
            'stock_status': not container.find(class_="product-card__in-stock product-card__in-stock--out _mt-xxs")
            },
        social_network="https://www.instagram.com/ukrarmor/",
        tel_vodafone="",
        tel_kyivstar=""
        ), 
    WebsiteScraper(
        name="UTactic",
        base_url="https://utactic.com/module/iqitsearch/searchiqit?s={query}",
        search_query_url="https://utactic.com/module/iqitsearch/searchiqit?s={query}",
        search_query_separator="+",
        product_container_class="js-product-miniature-wrapper",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product-title").text.strip(),
            'price': "".join(re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="product-price").text.strip()).group(0).split()),
            'stock_status': container.find(class_="product-price") != None
            },
        social_network="https://www.instagram.com/utactic_com/",
        tel_vodafone="+380991143045",
        tel_kyivstar="+380688631570"
        ), 
    WebsiteScraper(
        name="Velmet",
        base_url="https://velmet.ua/index.php?route=product/search&search={query}&page={page}",
        search_query_url="https://velmet.ua/index.php?route=product/search&search={query}",
        search_query_separator="",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find(class_="caption").find(class_="name").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip()).group(0).replace(" ",""),
            'stock_status': container.find(class_="status in_stock") != None
            },
        social_network="https://www.instagram.com/velmet.ua/",
        tel_vodafone="+380993738778",
        tel_kyivstar="+380673738778"
        ), 
    WebsiteScraper(
        name="Global Ballisticks",
        base_url="https://globalballistics.com.ua/ua/all-products/page-{page}?keyword={query}",
        search_query_url="https://globalballistics.com.ua/ua/all-products?keyword={query}",
        search_query_separator="+",
        product_container_class="product_item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product_preview__name_link").text.split("Артикул:")[0].strip(),
            'price': container.find(class_="price").find("span",class_="fn_price").text.strip().split(",")[0].replace(" ",""),
            'stock_status': not container.find(class_="product_preview__button product_preview__button--pre_order fn_is_preorder")
            },
        social_network="https://www.instagram.com/globalballistics/",
        tel_vodafone="+380662533086",
        tel_kyivstar="+380984377908"
        ), 
    WebsiteScraper(
        name="Grad Gear",
        base_url="https://gradgear.com.ua/katalog/search/filter/page={page}/?q={query}",
        search_query_url="https://gradgear.com.ua/katalog/search/filter/?q={query}",
        search_query_separator="+",
        product_container_class="catalog-grid__item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="catalogCard-title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(" ",""),
            'stock_status': container.find(class_="catalogCard-price") != None
            },
        social_network="https://www.instagram.com/grad.gear/",
        tel_vodafone="",
        tel_kyivstar="+380681437535"
        ), 
    WebsiteScraper(
        name="Tactical Systems",
        base_url="https://tactical-systems.com.ua/catalog/search/filter/page={page}/?q={query}",
        search_query_url="https://tactical-systems.com.ua/catalog/search/filter/?q={query}",
        search_query_separator="+",
        product_container_class="catalog-grid__item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="catalogCard-title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="catalogCard-price").text.strip()).group(0).replace(" ",""),
            'stock_status': not container.find(class_="catalogCard-price __light")
            },
        social_network="https://www.instagram.com/tactical_systems_ukraine/",
        tel_vodafone="",
        tel_kyivstar="+380675336474"
        ), 
    WebsiteScraper(
        name="Tur Gear",
        base_url="https://turgear.com.ua/page/{page}/?post_type=product&s={query}",
        search_query_url="https://turgear.com.ua/page/?post_type=product&s={query}",
        search_query_separator="%20",
        product_container_class="nm-shop-loop-product-wrap",
        extract_info_functions=lambda container: {
            'name': container.find(class_="woocommerce-loop-product__title").text.strip(),
            'price': re.search(r"\b\d*", container.find(class_="price").text.strip().split()[-1].replace(" ","")).group(0),
            'stock_status': container.find(class_="nm-shop-loop-actions") != None
            },
        social_network="https://www.instagram.com/turgear/",
        tel_vodafone="",
        tel_kyivstar=""
        ), 
    WebsiteScraper(
        name="UKRTAC",
        base_url="https://ukrtac.com/page/{page}/?s={query}&post_type=product&product_cat=0",
        search_query_url="https://ukrtac.com/?s={query}&post_type=product&product_cat=0",
        search_query_separator="+",
        product_container_class="product-grid-item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="wd-entities-title").text.strip(),
            'price': container.find(class_="price").text.strip().split()[-2],
            'stock_status': container.find(class_="hover-content-inner") != None and not container.find(class_="widget-product-wrap")
            },
        social_network="https://www.instagram.com/ukrtac/",
        tel_vodafone="",
        tel_kyivstar="+380980383800"
        ), 
    WebsiteScraper(
        name="Real Defence",
        base_url="https://real-def.com/all-products/page-{page}?keyword={query}",
        search_query_url="https://real-def.com/all-products/?keyword={query}",
        search_query_separator="+",
        product_container_class="product_item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product_preview__name").text.strip(),
            'price': container.find(class_="fn_price").text.strip().replace(" ",""),
            'stock_status': "Придбати" in container.find(class_="product_preview__order").text
            },
        social_network="https://instagram.com/real.defence/",
        tel_vodafone="",
        tel_kyivstar="+380673879659"
        ), 
    WebsiteScraper(
        name="AlphaBravo",
        base_url="https://alphabravo.com.ua/all-products/page-{page}?keyword={query}",
        search_query_url="https://alphabravo.com.ua/all-products/?keyword={query}",
        search_query_separator="+",
        product_container_class="product_item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="product_preview__name").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="fn_price").text.strip()).group(0).replace(" ",""),
            'stock_status': not container.find(class_="product_preview__button product_preview__button--buy alpha_btn fn_is_stock hidden-xs-up")
            },
        social_network="",
        tel_vodafone="+380663080308",
        tel_kyivstar="+380973380338"
        ), 
    WebsiteScraper(
        name="Avis Gear",
        base_url="https://avisgear.com/page/{page}/?s={query}&post_type=product",
        search_query_url="https://avisgear.com/page/?s={query}&post_type=product",
        search_query_separator="+",
        product_container_class="product-grid-item",
        extract_info_functions=lambda container: {
            'name': container.find(class_="wd-entities-title").text.strip(),
            'price': re.search(r"\b\d{1,3}(?:\s\d{3})*\b", container.find(class_="price").text.strip().replace(","," ")).group(0).replace(" ",""),
            'stock_status': not container.find(class_="product_preview__button product_preview__button--buy alpha_btn fn_is_stock hidden-xs-up")
            },
        social_network="https://instagram.com/avis_gear/",
        tel_vodafone="",
        tel_kyivstar=""
        ), 
    ]

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape websites for product information.")
    parser.add_argument("-n","--name", type=str, help="Name of the product to scrape. Use underscore instead of space between words: сумка_скидання")
    parser.add_argument("-j", "--json", help="Write output to JSON file in 'data' folder", action="store_true")  # Disabled by default if not passed
    parser.add_argument("-v", "--verbose", help="Display data after scraping", action="store_true")  # Disabled by default if not passed

    args = parser.parse_args()

    if not args.name:
        print("Error: Please provide a product name using the --name argument.")
        return
    elif not args.verbose and not args.json:
        print("Error: Conflicting flags. Script will not produce any output without --quiet or --json.")
        return
    
    # Replace multiple whitespace with a single one
    fmt_product_name = args.name.replace('_',' ').lower()
    
    # Start the timer
    start_time = time.time()
    
    # Aggregate data asynchronously
    result = asyncio.run(aggregate_data(websites, fmt_product_name, include_details=True))

    # Sorting the list of dictionaries based on 'price_uah_min'
    sorted_result = sorted(result, key=lambda x: x['price_uah_min'], reverse=False)  # Set reverse=True for descending order

    # Sorting the 'details' list within each dictionary based on 'price_uah'
    for entry in sorted_result:
        entry['details'] = sorted(entry['details'], key=lambda x: x['price_uah'], reverse=False)  # Set reverse=True for descending order
    
    if args.json:
        export_to_json(sorted_result)
     
    if args.verbose:
        display_scraped_data(sorted_result)
        
    # Print elapsed time
    check_time = time.time() - start_time
    print("⏱", f"Час пошуку: {check_time:.0f} сек.")


if __name__ == "__main__":
    main()