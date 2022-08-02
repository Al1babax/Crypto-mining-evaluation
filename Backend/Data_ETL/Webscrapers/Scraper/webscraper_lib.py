"""
Webscraper module
"""

# Imports
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


class WebScraper:

    def __init__(self, url: str, headless_mode: bool):
        # Setup variables
        self.url = url
        self.headless_mode = headless_mode

        # Setup browser options
        options = webdriver.ChromeOptions()
        options.headless = headless_mode
        options.add_argument("window-size=1920,1080")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # Webscraper start time
        self.start_time = dt.datetime.now()
        self.start_time_str = self.start_time.strftime("%Y-%m-%dT%H_%M_%S")

    def open_website(self):
        """
        Opens the website by given url

        :return:
        """
        self.driver.get(self.url)
        time.sleep(10)

    def make_element(self, selector_type, selector_value):
        """
        Give selector type and its value. Returns element that can is intractable using for example --> element.click()

        :param selector_type: XPATH/CSS/ID/CLASS_NAME
        :param selector_value: Selector value
        :return: element
        """

        if selector_type.lower() == "xpath":
            element = self.driver.find_element(by=By.XPATH, value=selector_value)
        elif selector_type.lower() == "css":
            element = self.driver.find_element(by=By.CSS_SELECTOR, value=selector_value)
        elif selector_type.lower() == "id":
            element = self.driver.find_element(by=By.ID, value=selector_value)
        elif selector_type.lower() == "class_name":
            element = self.driver.find_element(by=By.CLASS_NAME, value=selector_value)
        else:
            print("Selector type or selector_value was invalid")
            raise ValueError

        return element

    def get_sourcecode(self):
        data = self.driver.page_source
        return data

    def click_element(self, element):
        pass


