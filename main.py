import json
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
            prices = [int(product.price.split(' ')[0].replace(',', '')) for product in products]
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

            if include_details:
                # Include details only if include_details is True
                website_data["details"] = [
                    {
                        "product": product.name,
                        "price_uah": int(product.price.split(' ')[0].replace(',', ''))
                    }
                    for product in products
                ]

            # Append the website's data to the aggregated data list
            aggregated_data.append(website_data)

        print("-" * 40)  # Separator between websites

    return aggregated_data

# List of website instances
websites = [
    WebsiteScraper(
        name="Ataka",
        base_url="https://attack.kiev.ua/search/page-{page}?search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find("h4").find("a").text,
            'price': container.find(class_="price").text.strip(),
            'stock_status': not container.find("button", {"disabled": "disabled"})
            },
        social_network="https://www.facebook.com/ATAKA.kiev.ua/",
        tel_vodafone="+380955587673",
        tel_kyivstar="+380679305772"
        ),
    WebsiteScraper(
        name="Abrams",
        base_url="https://abrams.com.ua/ua/search/?search={query}&page={page}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find("h4").find("a").text,
            'price': container.find(class_="price").text.strip(),
            'stock_status': "Немає в наявності" not in container.find("div", class_="stock-status").text
            },
        social_network="https://www.instagram.com/abrams_reserve/",
        tel_vodafone="+380955216148",
        tel_kyivstar="+380688736587"
        )
    ]

# Dummy product name
product_name = "флісова шапка"


# Aggregate data and write to JSON file
result = aggregate_data(websites, product_name, include_details=False)
output_file_path = 'output.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(result, output_file, indent=2, ensure_ascii=False)

print(f"Data written to {output_file_path}")
