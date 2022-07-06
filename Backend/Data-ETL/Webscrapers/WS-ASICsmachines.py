from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
import json
import re
import pymongo
import datetime as dt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# Main function for webscraping machines


url = 'https://www.asicminervalue.com/'

time1 = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")


def main():
    try:
        number_of_profitable_prices=get_number_of__profitable_prices(url)
        dict_of_machines = {}
        list_of_machines=[]
        counter = 1
        link_of_machines = get_all_links_of_website_pages(url)
        for machine in link_of_machines[:number_of_profitable_prices]:
            dict_of_one_machine_spec={}
            dict_of_one_machine_spec = get_specs_from_website_table(
                url+machine[1:])
            dict_of_one_machine_spec['coins'] = get_minable_coin_of_machine(
                url+machine[1:])
            dict_of_one_machine_spec['available_stores'] = get_market_prices(
                url+machine[1:])
            dict_of_one_machine_spec['Algorithm_and_power'] = get_algorithm_of_one_machine(
                url+machine[1:])
            dict_of_one_machine_spec['available_mining_pools'] = get_available_mining_pools_of_one_machine(
                url+machine[1:])
            list_of_machines.append(dict_of_one_machine_spec)
            counter += 1
        time2=dt.datetime.now()
        print(counter)
        dict_of_machines['time'] = str(time1)
        dict_of_machines['data']=list_of_machines
        send_to_db(dict_of_machines)
    except:
        pass


# Selenium initliazing
def webscraper_id():
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920,1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) 
    return driver

# getting all machines link from the url page
def get_all_links_of_website_pages(url):
    source_code = requests.get(url)
    soup = BeautifulSoup(source_code.text, 'lxml')
    links_from_website = soup.find_all('a')
    link_of_machine_page = []
    for link in links_from_website:
        if 'miner' in link.get('href'):
            link_of_machine_page.append(link.get('href'))
    return link_of_machine_page


# Scrapping the spec from the website
def get_specs_from_website_table(url):
    source_code = requests.get(url)
    soup = BeautifulSoup(source_code.text, 'lxml')
    locate_div = soup.find('div', class_='col-sm-8')
    locate_table_from_div = locate_div.find(
        'table', class_='table table-striped')
    if locate_table_from_div is not None:
        specs = locate_table_from_div.find_all('tr')
        specs_label = locate_table_from_div.find_all('th')
        list_of_specs = []
        list_of_specs_label = []
        for spec in specs:
            spec_name = spec.find('td').text
            list_of_specs.append(spec_name)
        for label in specs_label:
            list_of_specs_label.append(label.text)
        dict_of_machines_spec = {}
        for ele in range(0, len(list_of_specs_label)):
            if list_of_specs_label[ele] !='Also known as':
                dict_of_machines_spec[list_of_specs_label[ele]] = list_of_specs[ele]
        return dict_of_machines_spec


# create a json file for prototype
def create_json_file(destination, dict):
    with open(destination, 'w+') as f:
        json.dump(dict, f, indent=5)


# get minable coins for one machine
def get_minable_coin_of_machine(url):
    source_code = requests.get(url)
    soup = BeautifulSoup(source_code.text, 'lxml')
    locate_div = soup.find_all('img', class_='img-responsive')
    list_of_minable_coins = []
    for i in locate_div:
        coin = i.get('title')
        if coin is not None:
            list_of_minable_coins.append(remove_b_tags(coin))
    return list_of_minable_coins

# remove <b> from one coins data


def remove_b_tags(string):
    left = re.search('<b>', string)
    left_index = left.span()[1]
    right = re.search('</b>', string)
    right_index = right.span()[0]
    return string[left_index:right_index]

# get market price and stores for one machine


def get_market_prices(url):
    driver = webscraper_id()
    driver.get(url)

    nb_of_stores = driver.find_elements(
        By.XPATH, '/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr')

    list_of_markets = []

    for counter in range(0, len(nb_of_stores)):
        try:
            name = driver.find_element(
                By.XPATH, '/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(counter+1)+']/td[2]/b/a')
            sleep(1)
            country = driver.find_element(By.XPATH, '/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(
                counter+1)+']/td[2]/span/img').get_attribute("data-original-title")
            sleep(1)
            price = driver.find_element(
                By.XPATH, '/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(counter+1)+']/td[3]/b')
            sleep(1)
            website_url = driver.find_element(
                By.XPATH, '/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(counter+1)+']/td[2]/b/a')
            sleep(1)
            dict_of_stores = {'name': name.text, 'country': country,
                            'price': price.text, 'website_link': website_url.get_attribute('href')}
            list_of_markets.append(dict_of_stores)
        except:
            pass
    driver.quit()
    return list_of_markets


def get_algorithm_of_one_machine(url):
    source_code = requests.get(url)
    scraper = BeautifulSoup(source_code.text, 'lxml')
    locate_table = scraper.find('table', {'class': 'table table-striped'})
    if locate_table is not None:
        locate_body = locate_table.find('tbody')
        locate_rows = locate_body.find_all('tr')
        machine_algos = {}
        for row in locate_rows:
            machine_algos['Algorithm_name'] = row.find('b').text
            list_of_usage = row.find('div').text.split(' ')
            machine_algos['hashrate'] = list_of_usage[0]
            machine_algos['power_consumption'] = list_of_usage[1]
        return machine_algos


def get_available_mining_pools_of_one_machine(url):
    source_code = requests.get(url)
    scraper = BeautifulSoup(source_code.text, 'lxml')
    locate_table = scraper.find(
        'table', {'class': 'table table-striped table-small'})
    if locate_table is not None:
        locate_body = locate_table.find('tbody')
        locate_rows = locate_body.find_all('tr')
        machine_available_pools = []
        for row in locate_rows:
            machine_available_pools_dict = {}
            machine_available_pools_dict['pool_name'] = row.find('b').text
            machine_available_pools_dict['url_link'] = row.find('a').get('href')
            machine_available_pools_dict['profit_type'] = row.find(
                'td', {'class': 'hidden-xs hidden-sm'}).find('b').text
            machine_available_pools.append(machine_available_pools_dict)
        return machine_available_pools





def send_to_db(dict):
    client=pymongo.MongoClient()
    mydb=client['Crypto-mining']
    asics=mydb['ASICS-PoW']
    if asics.find_one() != {}:
        asics.delete_many({})
        asics.insert_one(dict)


def get_number_of__profitable_prices(url):
    source_code=requests.get(url)
    soup=BeautifulSoup(source_code.text,'lxml')
    find_table=soup.find('table',{'id':'datatable_profitability'})
    find_body=find_table.find('tbody')
    find_row=find_body.find_all('tr')
    list_of_prices=[]
    for row in find_row:
        list_of_ele=row.text.split(' ')
        price=list_of_ele[-1].replace('$','')
        list_of_prices.append(list_of_ele[-1].replace('/day',' '))
    return len(list_of_prices)


# calling the main function
main()
