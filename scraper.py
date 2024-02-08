import json
import os
import time
import asyncio
import logging
import argparse

from web import websites


# Create logs path
log_file_path = os.path.join('logs', 'scraper.log')

# Set up logging
logging.basicConfig(filename=log_file_path, level=logging.WARNING, encoding='utf-8', filemode='w')


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