import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("DATA_SEOUL_APIKEY")

# Define the range of months and years
years = [2023, 2024]
months = list(range(1, 13))  # January to December

# Initialize an empty list to hold the data
all_data = []

# Function to fetch and parse data for a given year and month
def fetch_data(year, month):
    # Format the month to ensure two digits
    month_str = f"{month:02d}"
    date_str = f"{year}{month_str}"
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/xml/CardBusTimeNew/1/1000/{date_str}/"
    
    res = requests.get(url)
    
    if res.status_code == 200:
        root = ET.fromstring(res.content)
        data = []
        for item in root.findall('.//row'):
            record = {child.tag: child.text for child in item}
            data.append(record)
        return data
    else:
        print(f"Error: Unable to fetch data for {date_str}. Status code: {res.status_code}")
        return []

# Loop through each year and month to fetch the data
for year in years:
    for month in months:
        if year == 2023 or (year == 2024 and month in [1, 5]):
            data = fetch_data(year, month)
            all_data.extend(data)

# Convert the list of all records to a DataFrame
df = pd.DataFrame(all_data)

# Display the DataFrame
print(df)