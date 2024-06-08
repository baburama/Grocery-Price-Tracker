import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re
import os
import datetime
from pymongo import MongoClient

def fetch_price(url, item, store):
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load
    try:
        price_element = driver.find_element(By.XPATH, '//*[@id="site-content"]//span[contains(@class,"price") and not(contains(@class,"Price-per"))]')
        price_match = re.search(r"\d+\.\d+", price_element.text)
        if price_match:
            category = f"{store} {item}"
            price = float(price_match.group(0))
            # Get the current date
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            # Include the current date in the dictionary
            all_prices.append({"Date": current_date, "Category": category, "Item": item, "Store": store, "Price": price})
    except Exception as e:
        print(f"Error fetching price for {item} at {store}: {e}")

def print_all_prices(prices_list):
    for item in prices_list:
        print(f"{item['Item']} at {item['Store']}: ${item['Price']}")

def print_cheapest_prices(prices_list):
    unique_items = set(item['Item'] for item in prices_list)  # Identify all unique food items
    for item in unique_items:
        cheapest = min((i for i in prices_list if i['Item'] == item), key=lambda x: x['Price'])
        print(f"Cheapest {item}: {cheapest['Store']} at ${cheapest['Price']}")

def append_to_excel(df, filename):
    if os.path.exists(filename):
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            last_row = writer.sheets['Sheet1'].max_row
            df.to_excel(writer, index=False, header=False, startrow=last_row)
    else:
        df.to_excel(filename, index=False)

def update_prices(prices_list):
    for price in prices_list:
        filter = {"Item": price["Item"], "Store": price["Store"]}
        update = {
            "$set": {
                "Category": price["Category"],
                "Price": price["Price"],
                "Date": price["Date"]  # Update the date as well
            }
        }
        collection.update_one(filter, update, upsert=True)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.grocerydb
collection = db.prices

# Initialize WebDriver
service = Service(executable_path="chromedriverV25.exe")
driver = webdriver.Chrome(service=service)

# List to hold all prices
all_prices = []

# URLs and items to fetch
urls_items = [
    ("https://www.nofrills.ca/bananas-bunch/p/20175355001_KG", "Bananas", "No Frills"),
    ("https://www.loblaws.ca/bananas-bunch/p/20175355001_KG", "Bananas", "LobLaws"),
    ("https://www.realcanadiansuperstore.ca/bananas-bunch/p/20175355001_KG", "Bananas", "RCSS"),
    ("https://www.nofrills.ca/partly-skimmed-milk-2-mf/p/20188873_EA", "Milk", "No Frills"),
    ("https://www.loblaws.ca/partly-skimmed-milk-2-mf/p/20188873_EA", "Milk", "LobLaws"),
    ("https://www.realcanadiansuperstore.ca/partly-skimmed-milk-2-mf/p/20188873_EA", "Milk", "RCSS"),
    ("https://www.nofrills.ca/large-grade-a-eggs/p/20812144001_EA", "Eggs", "No Frills"),
    ("https://www.loblaws.ca/large-grade-a-eggs/p/20812144001_EA", "Eggs", "LobLaws"),
    ("https://www.realcanadiansuperstore.ca/large-grade-a-eggs/p/20812144001_EA", "Eggs", "RCSS"),
    ("https://www.nofrills.ca/thick-slices-bread/p/20038335_EA", "Bread", "No Frills"),
    ("https://www.loblaws.ca/thick-slices-bread/p/20038335_EA", "Bread", "LobLaws"),
    ("https://www.realcanadiansuperstore.ca/thick-slices-bread/p/20038335_EA", "Bread", "RCSS"),
]

# Fetch prices for each item at each store
for url, item, store in urls_items:
    fetch_price(url, item, store)

# Convert the populated all_prices list to DataFrame after fetching the data
df_prices = pd.DataFrame(all_prices)

# Close the WebDriver session
driver.quit()

# Print all collected prices and the cheapest options for comparison
print_all_prices(all_prices)
print_cheapest_prices(all_prices)

# Append the DataFrame to the Excel file
filename = 'prices_data_test.xlsx'
append_to_excel(df_prices, filename)

# Update prices in MongoDB
update_prices(all_prices)

# Verify by fetching and displaying data from MongoDB
stored_data = collection.find({}, {'_id': 0})  # exclude '_id' field from output
print("Data stored in MongoDB:")
for item in stored_data:
    print(item)

