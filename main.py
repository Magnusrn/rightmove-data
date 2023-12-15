import json
import sys
import time

import requests
from lxml import html
from datetime import datetime


def main(link):
    file_path = 'prices.json'
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_data = read_json_file(file_path)
    link = str(link)

    if link in json_data:

        latest_price = json_data[link][-1]['price']
        json_data = format_to_json(link, latest_price, date, json_data)
    else:
        initial_price = get_current_price_from_link(link)
        json_data[link] = [{'price': initial_price, 'date': date}]

    write_json_file(file_path, json_data)


def query_and_update_json():
    # Load the JSON data from the file
    with open('prices.json', 'r') as file:
        data = json.load(file)
    # Iterate over each link and print it
    for link in data.keys():
        main(link)
        time.sleep(5)
        print(f"Updating Link: {link}")


def format_to_json(link, last_price, date, json_data):
    current_price = get_current_price_from_link(link)
    if current_price != last_price:
        data = {
            "price": current_price,
            "date": date}
        json_data[link].append(data)
    return json_data


def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # if it's empty json(though i guess this would also delete a corrupted json so should backup)
            except json.decoder.JSONDecodeError:
                return {}
        return data
    except FileNotFoundError:
        return {}


def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def get_current_price_from_link(link):
    # Send an HTTP request to the URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/62.0.3202.94 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
    }
    response = requests.get(link, headers=headers,
                            timeout=10)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using lxml
        tree = html.fromstring(response.content)
        # Use XPath to extract data
        price = tree.xpath('//*[@id="root"]/main/div/div[2]/div/article[1]/div[2]/div/div[1]/span[1]')[0].text
        # Remove non-numeric characters (including currency symbols and commas)
        return int(''.join(c for c in price if c.isdigit()))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(f"Usage: python script.py {sys.argv[1]}")
        main(sys.argv[1])
    # #else check all links in json and update
    else:
        query_and_update_json()
