#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
options.headless = False
options.add_argument("window-size=1920,1080")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
start_url = "https://coolparcel.com/shipping/international/shipping-calculator"
wait = WebDriverWait(driver, 1)
time1 = dt.datetime.now()
current_time = time1.strftime("%Y-%m-%dT%H_%M_%S")


# In[20]:


def element_by_id(id1:str):
    element = driver.find_element(by=By.ID, value=id1)
    return element


# In[21]:


def element_by_selector(selector:str):
    element = driver.find_element(by= By.CSS_SELECTOR, value=selector)
    return element


# In[22]:


def country_info_input(country:str, postalcode:str, from1 = False):
    # Setup input field variables
    country_input = element_by_id("package-input-origin") if from1 else element_by_id("package-input-destination")
    postal_input = element_by_id("package-origin_postcode") if from1 else element_by_id("package-delivery_postcode")

    # Write country
    country_input.click()
    time.sleep(1)
    country_input.send_keys(Keys.BACKSPACE)
    time.sleep(1)
    country_input.send_keys(country)
    time.sleep(1)

    # Write postalcode
    postal_input.send_keys(postalcode)


# In[23]:


def setup_search(countries:list, postalcodes:list, from1:list, package_specs:dict):
    """
    :param countries: List of origin and destination countries
    :param postalcodes: List of postalcodes from origin and destination
    :param from1: List that specifies if first or second country is origin
    :param package_specs: Example input {"weight":"20", "length":"20", "width":"30", "height":"5"} -- Weight in lb(pounds), length measurements in In(inches)
    :return
    """
    # Loop through and setup countries input fields
    for index, country in enumerate(countries):
        country_info_input(country, postalcodes[index], from1[index])
        time.sleep(1)

    # Setup measurement variables
    weight = element_by_selector("#clone-package-container > div > div > div:nth-child(1) > div > div.form-group.col-6.col-lg-6 > div > input")
    length = element_by_selector("#clone-package-container > div > div > div:nth-child(2) > div > div:nth-child(1) > div > input")
    width = element_by_selector("#clone-package-container > div > div > div:nth-child(2) > div > div:nth-child(2) > div > input")
    height = element_by_selector("#clone-package-container > div > div > div:nth-child(2) > div > div:nth-child(3) > div > input")

    # Open custom measurements
    size_button = element_by_id("package-custom-size")
    # driver.execute_script("arguments[0].scrollIntoView();", size_button)
    time.sleep(1)
    size_button.click()
    time.sleep(1)

    # Setup measurements input fields
    weight.send_keys(package_specs["weight"])
    time.sleep(1)
    length.send_keys(package_specs["length"])
    time.sleep(1)
    width.send_keys(package_specs["width"])
    time.sleep(1)
    height.send_keys(package_specs["height"])
    time.sleep(1)

    # Click search
    find_price = element_by_selector("#package > form > div.details-packages > div.find-price > button")
    find_price.click()


# In[24]:


def scrape_data():
    info_container = driver.find_elements(by=By.CLASS_NAME, value="result-container")
    result = [x.text for x in info_container]
    return result


# In[25]:


def jsonfy_data(data, from1, to1):  # Going through data taking some info --> turning into dataframe --> lastly to record json for mongodb
    all_data = []
    for shipment in data:
        temp_data = shipment.split("\n")
        temp_dict = {"time":current_time, "from":from1, "to":to1}
        for index, line in enumerate(temp_data):
            if " → " in line:
                temp_dict["delivery_method"] = line
            elif index == 1:
                temp_dict["company"] = line
            elif "$" in line:
                temp_dict["cost"] = line
        all_data.append(temp_dict)

    df = pd.DataFrame(all_data)
    return df


# In[26]:


def push_to_mongodb(data):  # TODO mongodb write
    pass


# In[81]:


def check_init_input(from1, to1, package_measures):
    country_list = []
    us_states_list = []
    with open("resources/countries_list.txt") as r, open("resources/us_states.txt") as r2:
        for country in r.readlines():
            country_list.append(country[:-1])

        for state in r2.readlines():
            us_states_list.append(state[:-1])

    print(us_states_list)
    # Checking if countries exists
    if (from1.capitalize() in country_list and to1.capitalize() in country_list) or (from1 in us_states_list and to1 in us_states_list):
        # Checking that package_measures have all the info
        measurements = ["weight", "length", "width", "height"]
        for measurement in measurements:
            if measurement in package_measures.keys():
                pass
            else:
                print("Measurements wrong")
                return False

        for k, v in package_measures.items():
            try:
                float(v)
            except ValueError as e:
                print(e)
                print("Given item measurement format is wrong")

        return True
    else:
        return False


# In[129]:


def get_zipcode(country):
    # get zipcode for country or us state
    if country.lower() == "finland":
        return "00100"

    df = pd.read_json("resources/uszips.json")
    zip_code = df[df["state_name"] == country]["zip"].iloc[3]
    if len(str(zip_code)) == 3:
        return "00" + str(zip_code)
    elif len(str(zip_code)) == 4:
        return "0" + str(zip_code)
    else:
        return str(zip_code)


# In[27]:


def main(from1, to1, package_measures):
    time.sleep(3)
    driver.get(start_url)
    time.sleep(10)
    setup_search([from1, to1], ["8000", "00100"], [True, False], {"weight":"20", "length":"20", "width":"30", "height":"5"}) # TODO setup zipcode check from database and using get_zipcode() function
    time.sleep(20)
    raw_data = scrape_data()
    df = jsonfy_data(raw_data, from1, to1)
    push_to_mongodb(df)
    driver.quit()


# In[ ]:


def init(from1:str, to1:str, package_measures:dict):
    try:
        check_init_input(from1, to1, package_measures)
        main(from1, to1, package_measures)
    except:
        print("Unexpected error")

