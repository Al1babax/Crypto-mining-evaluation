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

url = 'https://www.asicminervalue.com/'

time1 = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")

client = pymongo.MongoClient()
mydb = client['Crypto-mining']
# main function to scrape machines data


def main():
    dict_of_machines = {}
    list_of_machines = []
    counter = 1
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    }
    link_of_machines = get_all_links_of_website_pages(url)
    for machine in link_of_machines[:len(link_of_machines) - 1]:
        try:
            source_code = requests.get(
                url + machine[1:], headers=headers, timeout=10)
            dict_of_one_machine_spec = {}
            dict_of_one_machine_spec = get_specs_from_website_table(
                source_code)
            dict_of_one_machine_spec['coins'] = get_minable_coin_of_machine(
                source_code)
            dict_of_one_machine_spec['available_stores'] = get_market_prices(
                source_code)
            dict_of_one_machine_spec['Algorithm_and_power'] = get_algorithm_of_one_machine(
                source_code)
            dict_of_one_machine_spec['available_mining_pools'] = get_available_mining_pools_of_one_machine(
                source_code)
            list_of_machines.append(dict_of_one_machine_spec)
            counter += 1
            print(counter)
        except:
            pass
    asics = mydb['ASICS-PoW-final']
    dict_of_machines['time'] = str(time1)
    dict_of_machines['data'] = list_of_machines
    send_to_db(dict_of_machines, asics)
    return time1


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
def get_specs_from_website_table(sc):
    source_code = sc
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
            if list_of_specs_label[ele] != 'Also known as':
                if list_of_specs_label[ele] == 'Weight':
                    list_of_specs_label[ele] += '(g)'
                else:
                    if list_of_specs_label[ele] == 'Size':
                        list_of_specs_label[ele] += '(mm)'
                    else:
                        if list_of_specs_label[ele] == 'Power':
                            list_of_specs_label[ele] += '(w)'
                dict_of_machines_spec[list_of_specs_label[ele]] = extract_numbers_from_specs(
                    list_of_specs_label[ele], list_of_specs[ele])
        return dict_of_machines_spec


# create a json file for prototype
def create_json_file(destination, dict):
    with open(destination, 'w+') as f:
        json.dump(dict, f, indent=5)


# get minable coins for one machine
def get_minable_coin_of_machine(sc):
    source_code = sc
    soup = BeautifulSoup(source_code.text, 'lxml')
    locate_div = soup.find_all(
        'div', {'style': 'padding:4px;float:left;width:60px;height:60px;'})
    if locate_div is not None:
        list_of_minable_coins = []
        for i in locate_div:
            coin = i.find('img', {'class': 'img-responsive'}).get('title')
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
def get_market_prices(sc):
    source_code1 = sc
    list_of_markets = []
    soup = BeautifulSoup(source_code1.text, 'lxml')
    find_table = soup.find('table', {'id': 'datatable_opportunities'})
    if find_table is not None:
        find_body = find_table.find('tbody')
        find_row = find_body.find_all('tr')
        for row in find_row:
            dict_of_stores = {}
            price_loc = row.find('td', {
                'class': 'text-center', 'style': 'vertical-align: middle;  width:180px; font-size:1.2em;'})
            dict_of_stores['store_name'] = row.find('b').text
            dict_of_stores['url'] = row.find('a').get('href')
            dict_of_stores['price'] = price_loc.find('b').text
            dict_of_stores['country'] = row.find(
                'span', {'style': 'float:right;text-align:center;'}).find('img').get('title')
            dict_of_stores['stock'] = row.find(
                'td', {'class': 'text-center', 'style': 'vertical-align: middle; font-size:1.1em;'}).text
            price_type = row.find('td', {'class': 'text-center hidden-xs hidden-sm',
                                  'style': 'vertical-align: middle; font-size:1.1em;'}).text[:14]
            if price_type == 'Free Shipping':
                dict_of_stores['isFreeShipping'] = True
            else:
                dict_of_stores['isFreeShipping'] = False
            list_of_markets.append(dict_of_stores)

        return list_of_markets


# get algorithms of each machine
def get_algorithm_of_one_machine(sc):
    source_code = sc
    list_of_algo = []
    scraper = BeautifulSoup(source_code.text, 'lxml')
    locate_table = scraper.find('table', {'class': 'table table-striped'})
    if locate_table is not None:
        locate_body = locate_table.find('tbody')
        locate_rows = locate_body.find_all('tr')
        for row in locate_rows:
            machine_algos = {}
            try:
                machine_algos['Algorithm_name'] = row.find('b').text
                list_of_usage = row.find('div').text.split(' ')
                machine_algos['hashrate(H/second) '] = convert_to_hash_per_hour(
                    extract_numbers(list_of_usage[0]), extract_unit_from_string(list_of_usage[0]))
                machine_algos['power_consumption(W)'] = extract_numbers(
                    list_of_usage[1])
                list_of_algo.append(machine_algos)
            except:
                pass
        return list_of_algo


# convert to h/s
def convert_to_hash_per_second(amount, unit):
    if unit == 'kh/s':
        amount *= 1_000
    else:
        if unit == 'mh/s':
            amount *= 1_000_000
        else:
            if unit == 'gh/s':
                amount *= 1_000_000_000
            else:
                if unit == 'th/s':
                    amount *= 1_000_000_000_000
                else:
                    if unit == 'ph/s':
                        amount *= 1_000_000_000_000_000
                    else:
                        if unit == 'eh/s':
                            amount *= 1_000_000_000_000_000_000
    return amount


# convert from h/s to h/hour
def convert_to_hash_per_hour(amount, unit):
    return convert_to_hash_per_second(amount, unit)


# extract numbers from a string

def extract_numbers(string):
    new_string = ''
    for i in string:
        if i in '1234567890.%':
            new_string = new_string + i
    if '%' in new_string:
        new_string = new_string.replace('%', '')
        return float(new_string) / 100
    try:
        return float(new_string)
    except:
        return string


# extract unit from a string for conversion
def extract_unit_from_string(string):
    finder = 0
    for i in range(0, len(string)):
        if string[i] not in '1234567890.':
            finder = i
            break
    return string[finder:].lower()


# get available mining pools for each machine
def get_available_mining_pools_of_one_machine(sc):
    source_code = sc
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
            machine_available_pools_dict['url_link'] = row.find(
                'a').get('href')
            machine_available_pools_dict['profit_type'] = row.find(
                'td', {'class': 'hidden-xs hidden-sm'}).find('b').text
            machine_available_pools_dict['profit_perc'] = extract_numbers(row.find(
                'td', {'class': 'hidden-xs hidden-sm'}).text)
            machine_available_pools.append(machine_available_pools_dict)
        return machine_available_pools

# Migrate data to database


def send_to_db(liste, collection):
    collection.insert_one(liste)


# turn some specs value into integer
def extract_numbers_from_specs(label_name, val):
    if label_name == 'Size(mm)':
        res = val.split('x')
        dimension = {'x': float(res[0]), 'y': float(
            res[1]), 'z': extract_numbers(res[2])}
        return dimension
    else:
        if label_name == 'Weight(g)' or label_name == 'Power(w)':
            return extract_numbers(val)
    return val


# calling the main function
if __name__ == '__main__':
    main()
