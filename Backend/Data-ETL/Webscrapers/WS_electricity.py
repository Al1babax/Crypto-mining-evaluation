#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import selenium.common.exceptions
from selenium import webdriver
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
import os
import numpy as np
import pymongo

# Settings
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920,1080")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
start_url = "https://vare.fi/sahkosopimus/porssisahko/"
usa_url = "https://www.energybot.com/electricity-rates-by-state.html"
wait = WebDriverWait(driver, 1)
time1 = dt.datetime.now()
current_time = time1.strftime("%Y-%m-%dT%H_%M_%S")


# In[2]:


def element_by_id(id1: str):
    element = driver.find_element(by=By.ID, value=id1)
    return element


def element_by_selector(selector: str):
    element = driver.find_element(by=By.CSS_SELECTOR, value=selector)
    return element


# In[3]:


def finland_electricity():
    time.sleep(3)
    driver.get(start_url)
    time.sleep(20)
    info_box = element_by_selector(
        "#blokki-3 > div > section > div > div > div.column.is-6-desktop.is-offset-1-desktop > div > div > div.hourly-prices-chart-data > div.hourly-prices-chart-data-pricecards.mb-4")
    daily_info = element_by_selector(
        "#blokki-3 > div > section > div > div > div.column.is-6-desktop.is-offset-1-desktop > div > div > div.hourly-prices-chart-data > div.hourly-prices-chart-average-prices")

    overall_info_list = info_box.text.split("\n")
    daily_info_list = daily_info.text.split("\n")

    # Finding all the prices from elements
    current_price = float(overall_info_list[1].split(" ")[0].replace(",", ".")) + 0.25
    day_average = float(daily_info_list[0].split(":")[1].lstrip().split(" ")[0].replace(",", ".")) + 0.25
    night_average = float(daily_info_list[1].split(":")[1].lstrip().split(" ")[0].replace(",", ".")) + 0.25
    yearly_average = float(overall_info_list[-2].split(" ")[0].replace(",", ".")) + 0.25

    data = [{"currency": "cent/kWh €", "current_price": current_price, "day_average": day_average,
             "night_average": night_average, "yearly_average": yearly_average, "electricity_company_cut": 0.25}]
    df2 = pd.DataFrame(data)
    return df2


# In[4]:


def usa_electricity():
    driver.get(usa_url)
    time.sleep(20)
    data = element_by_selector(
        "body > div.eb-state-container > div > div.eb-landing-page-container > div.html-embed-scroll.w-embed")

    state_data = data.text.split("\n")[3:]
    all_data = []
    for state in state_data:
        temp_data = {"currency": "cent/kWh $"}
        temp_info = state.split(" ")

        while temp_info[1].isalpha():
            temp_info[0] += " " + temp_info[1]
            temp_info.pop(1)

        # Setup all info to dict
        temp_data["state"] = temp_info[0]
        temp_data["current_month"] = temp_info[1]
        temp_data["previous_month"] = temp_info[2]
        temp_data["change (%)"] = temp_info[3]

        all_data.append(temp_data)

    df3 = pd.DataFrame(all_data)
    return df3


# In[5]:


def write_mongodb(df1, df2, time1):
    client = pymongo.MongoClient()
    db = client["Electricity"]

    # USA database write
    collection = db["USA"]
    collection.insert_one({"date": time1, "data": df2.to_dict(orient="records")})

    # Finland database write
    collection = db["Finland"]
    collection.insert_one({"date": time1, "data": df1.to_dict(orient="records")})


# In[6]:


def main(time1):
    start_time = dt.datetime.now()
    finland_df = finland_electricity()
    usa_df = usa_electricity()
    write_mongodb(finland_df, usa_df, time1)
    driver.quit()
    print(f"Runtime: {dt.datetime.now() - start_time} seconds")

