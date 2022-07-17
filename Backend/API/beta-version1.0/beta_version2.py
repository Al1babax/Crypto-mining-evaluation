from fastapi import FastAPI
from numpy import sort
import pymongo
import json
from sorting import merge
import sorting_machines

client = pymongo.MongoClient()
machine_db = client['Crypto-mining']
electricity_db = client['Electricity']
coin_data = client['Coin-Data']
my_col_coin = coin_data['sortet_coin']
my_col_electricy_us = electricity_db['USA']


def token_used():
    return ['Bitcoin', 'BTC']


def get_elec_price(state, my_col):
    states = my_col.find({}, {'_id': 0, 'date': 0})
    for statse in states:
        list_state = statse

    for ind in range(0, len(list_state['data'])):
        if list_state['data'][ind]['state'] == state:
            return float(list_state['data'][ind]['current_month'])/100


def get_token_reward_from_db(coin, my_col):
    query = {'name': token_used()[0]}
    return my_col.find_one(query)['profit/hash/hour']


def get_shipping_price(Size: list, weight: float):
    return 100


def extract_symboles_from_price(price: str):
    price2 = price.replace('$', '')
    price3 = price2.replace(',', '')
    return price3


def get_one_machine_profit(machine: dict):
    income = machine['algo']['hashrate(H/hour) '] * \
        get_token_reward_from_db(token_used()[0], my_col_coin)*720
    if machine['stores']['isFreeShipping'] == False:
        outcome = float(extract_symboles_from_price(machine['stores']['price']))+float((get_elec_price('Alaska', my_col_electricy_us))/1000) * \
            720*float(machine['algo']['power_consumption(W)']
                      )  # power price per month
        outcome = outcome + \
            get_shipping_price(machine['size'], machine['weight'])
    else:
        outcome = float(extract_symboles_from_price(machine['stores']['price']))+float((get_elec_price('Alaska', my_col_electricy_us))/1000) * \
            720*float(machine['algo']['power_consumption(W)']
                      )  # power price per month

    return {'time_to_profit': outcome/income, 'profit_after_per_months': income}


def find_best_algo(liste):
    return sort(liste)[0]


def find_stores(machine):
    data = machine['available_stores']
    res = []
    for store in data:
        if store['stock'] != 'Out of stock':
            res.append(store)
            break
    return res


def get_machines_from_db(algorithm):
    asics = machine_db['ASICS-PoW2']
    query = {'Algorithm_and_power.Algorithm_name': algorithm}
    data = asics.find(query)
    list_of_machines = []
    for machine in data:
        try:
            dict = {}
            dict['name'] = machine['Manufacturer']+machine['Model']
            dict['size'] = [
                machine['Size(mm)']['x'], machine['Size(mm)']['y'], machine['Size(mm)']['z']]
            dict['weight'] = machine['Weight(g)']
            dict['algo'] = find_best_algo(machine['Algorithm_and_power'])
            dict['stores'] = find_stores(machine)[0]
            dict['full_profit'] = get_one_machine_profit(dict)
            list_of_machines.append(dict)
        except:
            pass
    return list_of_machines


def sort_machines():
    return sorting_machines.merge(get_machines_from_db('SHA-256'))
