import asyncio
import logging
import time
import os

from lib.websites_list import websites   # list of WebsiteScraper objects


# Create logs path
log_file_path = os.path.join('logs', 'generate_result.log')

# Set up logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.WARNING,
    encoding='utf-8',
    filemode='a',
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def async_scrape(website, product_name):
    """
    Asynchronously scrape data from a website

    Args:
        website (str): website name
        product_name (str): name of the product to look for

    Returns:
        dict: dictionary with scraped prices for a given product from an input website 
    """
    logging.debug(f"Scraping data from {website.name}...")

    # Use asyncio.to_thread to run the synchronous scrape method in a separate thread
    products = await asyncio.to_thread(website.scrape, product_name)

    return website, products


async def aggregate_data(websites, product_name):
    """
    Aggregate data from multiple websites based on a given product.

    Parameters:
    - websites: list of WebsiteScraper objects, websites to scrape data from
    - product_name: str, the product to search for

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
                prices = sorted([int(product.price) for product in products])

                price_uah_min = prices[0]
                price_uah_max = prices[-1]

            except ValueError:
                # Log an error if conversion of price to integer was unsuccessful
                logging.error("Conversion of price to integer was unsuccessful. Storing as a string...")
                prices = [product.price for product in products]
                logging.error("Got price (-s)", prices[0])

            except Exception as e:
                logging.error("Unexpected error: ", e)

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


def format_scraped_data(sorted_result, product_name):
    """
    This function formats scraped data into a single string used in the response message.

    Args:
        sorted_result (list): List of dictionaries containing website data.
        product_name (str): A searched product name used at the beginning of the response.

    Returns:
        str: Formatted message with website names, product quantities, and prices.
    """
    formatted_message = ""
    total_products_qty = sum(website["products_qty"] for website in sorted_result)

    # Add searched product name
    formatted_message += f"<b>{product_name}</b>\n"
    
    # Add total products count
    formatted_message += f"Знайдено товарів: {total_products_qty}\n\n"

    # Add details for each website
    for website in sorted_result:
        formatted_message += f"<b>{website['website']}</b>\n"
        formatted_message += f"◽ К-сть: {website['products_qty']} шт.\n"

        if website["price_uah_min"] == website["price_uah_max"]:
            formatted_message += f"◽ Ціна: {website['price_uah_min']:,} грн.\n"
        else:
            formatted_message += f"◽ Ціна: {website['price_uah_min']:,} -- {website['price_uah_max']:,} грн.\n"

        formatted_message += f"<a href='{website['search_query_url']}'>перейти→</a>\n\n"

    return formatted_message


async def generate_formatted_output(product_name):
    """
    Main scraper function which is used to scrape prices for a given product.

    Args:
        product_name (str): product to scrape prices for

    Returns:
        str: html formated string containing the scraped prices for a product
    """

    # Start the timer
    start_time = time.time()

    # Aggregate data asynchronously
    result = await aggregate_data(websites, product_name)

    # Sorting the list of dictionaries based on 'price_uah_min'
    sorted_result = sorted(result, key=lambda x: x['price_uah_min'], reverse=False)  # Set reverse=True for descending order

    # Sorting the 'details' list within each dictionary based on 'price_uah'
    for entry in sorted_result:
        entry['details'] = sorted(entry['details'], key=lambda x: x['price_uah'], reverse=False)  # Set reverse=True for descending order

    # Format scraped data
    formated_output =  format_scraped_data(sorted_result, product_name)
    
    # Display elapsed time
    check_time = time.time() - start_time
    formated_output += f"⏱ Час пошуку: {check_time:.0f} сек."
    
    return formated_output