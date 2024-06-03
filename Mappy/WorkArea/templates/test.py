import os
import requests
import json
import xmltodict
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DATA_SEOUL_APIKEY")
service_name = "CardBusTimeNew"
service_url = f"http://openapi.seoul.go.kr:8088/{api_key}/xml/CardBusTimeNew/"

def response_to_dict(res):
    return json.loads(json.dumps(xmltodict.parse(res.text)))

def get_list_total_count(date):
    url = service_url + '1/1/' + date
    res = requests.get(url)
    res_dict = response_to_dict(res)
    if 'CardBusTimeNew' in res_dict:
        list_total_count = int(res_dict['CardBusTimeNew']['list_total_count'])
        return list_total_count
    else:
        return 0

def get_call_range_list(list_total_count):
    call_range_list = []
    call_capacity = 1000
    q = list_total_count // call_capacity
    r = list_total_count % call_capacity
    
    for i in range(q):
        start_index = i * call_capacity + 1
        last_index = (i + 1) * call_capacity   
        call_range_list.append(f'{start_index}/{last_index}/')

    if r != 0:
        start_index = q * call_capacity + 1
        last_index = list_total_count   
        call_range_list.append(f'{start_index}/{last_index}/')

    return call_range_list

def get_date_str_list(from_date, to_date, freq='M'):
    date_list = []

    period_range = pd.period_range(from_date, to_date, freq=freq).to_timestamp()

    for date in period_range:
        date_str = date.strftime('%Y%m')
        if freq == 'D':
            date_str = date.strftime('%Y%m%d')
        date_list.append(date_str)

    return date_list

def fetch_data_for_date(date):
    list_total_count = get_list_total_count(date)
    if list_total_count == 0:
        return []  
    call_range_list = get_call_range_list(list_total_count)
    
    all_data = []
    for call_range in call_range_list:
        url = service_url + call_range + date
        res = requests.get(url)
        res_dict = response_to_dict(res)
        if 'CardBusTimeNew' in res_dict and 'row' in res_dict['CardBusTimeNew']:
            items = res_dict['CardBusTimeNew']['row']
            all_data.extend(items)
    
    return all_data

date_str_list = get_date_str_list('202301', '202404', 'M')

all_data = []
for date in date_str_list:
    data = fetch_data_for_date(date)
    all_data.extend(data)

df = pd.DataFrame(all_data)

print(df)
