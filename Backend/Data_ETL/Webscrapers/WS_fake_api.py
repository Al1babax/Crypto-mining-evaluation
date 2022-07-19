#!/usr/bin/env python
# coding: utf-8

# # This only needs to be run once --> collects coin mining difficulty from 2013 to 2022

# In[185]:


import requests
import pandas as pd
import selenium.common.exceptions
# from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import datetime as dt
import time
import re
import pymongo
import json
from fake_useragent import UserAgent
from seleniumwire import webdriver

options2 = {
    'disable_encoding': True  # Ask the server not to compress the response
}

# Settings
options = webdriver.ChromeOptions()
options.headless = True
ua = UserAgent()
userAgent = ua.chrome
options.add_argument(f"user-agent={userAgent}")
options.add_argument('--window-size=1920,1080')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, seleniumwire_options=options2)
wait = WebDriverWait(driver, 1)
time1 = dt.datetime.now()
current_time = time1.strftime("%Y-%m-%dT%H_%M_%S")
client = pymongo.MongoClient()


# In[186]:


def read_data(list1):
    all_data = []
    for item in list1:
        temp_dict = {
            "date": dt.datetime.utcfromtimestamp((int(item[0])/1000)).strftime('%Y-%m-%d'),
            "difficulty": int(item[1])
        }
        all_data.append(temp_dict)

    df = pd.DataFrame(all_data)
    return df


# In[187]:


def get_links():
    result = requests.get("https://www.coinwarz.com/charts/difficulty-charts")
    print(result)
    doc = BeautifulSoup(result.text, "lxml")
    tag = doc.find(text="Most Popular Cryptocurrency Difficulty Charts").parent.parent
    lines = tag.find_all("img")

    all_coins = []
    for line in lines:
        final = re.findall("alt=\S+", str(line))[0].split('"')[1]
        # print(final)
        all_coins.append(final.lower())

    return all_coins


# In[188]:


def fake_api_request(link):
    url = f"https://www.coinwarz.com/mining/{link}/difficulty-chart"
    driver.get(url)
    time.sleep(10)

    for request in driver.requests:
        if request.url == "https://www.coinwarz.com/ajax/diffchartdata":
            a_byte = request.response.body
            a_str = str(a_byte)[2:-1]
            res = json.loads(a_str)
            return res


# In[189]:


def write_database(coin_df:pd.DataFrame, coin_name):
    db = client["Coin-Data"]
    col = db[coin_name]
    col.insert_one({"date": current_time, "data":coin_df.to_dict(orient="records")})


# In[190]:


def main():
    links = get_links()
    for link in links:
        print(f"Scraping {link} data...")
        data = fake_api_request(link)
        df = read_data(data)
        write_database(df, link)
        print(f"Scraping {link} done")
    driver.quit()


# In[191]:


if __name__ == '__main__':
    main()

