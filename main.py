from websitescraper import WebsiteScraper

# List of website instances
websites = [
    WebsiteScraper(
        base_url="https://attack.kiev.ua/search/page-{page}?search={query}",
        search_query_separator="%20",
        product_container_class="product-layout",
        extract_info_functions=lambda container: {
            'name': container.find("h4").find("a").text,
            'price': container.find(class_="price").text.strip(),
            'stock_status': not container.find("button", {"disabled": "disabled"})
        }
    ),
    # Add more websites as needed
]

# Dummy product name
product_name = "патч"

# Iterate over websites and scrape data
for website in websites:
    print(f"\nScraping data from {website.base_url}...\n")
    products = website.scrape(product_name)
    for product in products:
        print(product)
    print("-" * 40)  # Separator between websites