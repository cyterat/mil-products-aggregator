import csv
import os
from datetime import datetime


def generate_bot_usage_data(data_dir, chat_id):
    """
    Appends a new row with 'chat_id' and current timestamp to a CSV file.

    Parameters:
        - data_dir (str): The path to the CSV file.
        - chat_id: The chat ID value to be appended to the CSV file.

    If the CSV file does not exist, it will be created with a header row containing 'chat_id' and 'timestamp'.
    If the file already exists, a new row will be appended with the provided 'chat_id' and the current date and time.

    Example:
        append_to_csv('path/to/your/file.csv', '123456')
    """
    # Check if the file exists to determine whether to write the header
    file_exists = os.path.isfile(data_dir)
    
    # Get current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(data_dir, mode='a', newline='') as f:
        writer = csv.writer(f)

        # Write header if the file is newly created
        if not file_exists:
            writer.writerow(['chat_id', 'timestamp'])

        # Write the chat_id and timestamp
        writer.writerow([chat_id, current_datetime])