#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pymongo
import utility.currency_conversion_rate as ccr
import datetime as dt

# # Things to note in calculating current profit
# - Expenses
# -- Machine price
# -- Shipment cost
# -- Taxes
# -- Electricity price
# -----------------------------------
# - Revenue
# -- Profit per mining power per hour

# In[2]:


client = pymongo.MongoClient()
pd.set_option("mode.chained_assignment", None)
eur_to_dollar_rate = 1  # placeholder


def get_coin_data():
    # Coin database
    col = client["Coin-Data"]["Current_coin"]
    sort = list({'_id': -1}.items())
    result = col.find(sort=sort, limit=1)

    coin_df = pd.DataFrame(result[0]["data"])
    return coin_df


# In[11]:


def get_machines_data():
    # Machine database
    col = client["Crypto-mining"]["ASICS-PoW-final"]
    sort = list({'_id': -1}.items())
    result = col.find(sort=sort, limit=1)

    machine_df = pd.DataFrame(result[0]["data"])
    return machine_df


# In[12]:


def currency_conversion_rate():
    global eur_to_dollar_rate
    rates = ccr.get_currency_ratio()
    eur_to_dollar_rate = rates["us(dollar)"]


# In[13]:


def get_electricity_data(country):
    """
    Takes country and returns dollar/kWh
    For example takes "Finland" and returns 0.15 dollar/kWh
    :param country:
    :return:
    """
    # Electricity database
    if country == "Finland":
        col = client["Electricity"]["Finland"]
        sort = list({'_id': -1}.items())
        result = col.find(sort=sort, limit=1)

        electricity_df = pd.DataFrame(result[0]["data"])
        return (electricity_df.iloc[0, 4] / 100) * eur_to_dollar_rate

    col = client["Electricity"]["USA"]
    sort = list({'_id': -1}.items())
    result = col.find(sort=sort, limit=1)

    electricity_df = pd.DataFrame(result[0]["data"])
    electricity_df = electricity_df[electricity_df["state"] == country]
    if len(electricity_df) == 1:
        return float((electricity_df.iloc[0, 2])) / 100


# In[23]:


def dataframe_for_algo(algo, country):
    # Get all the databases needed for profit calculation without shipping/taxes
    coin_df = get_coin_data()

    # Modify dataframes
    coin_df["algorithm"] = coin_df["algorithm"].apply(lambda x: x.lower())

    # Make variables
    algo_name = algo["Algorithm_name"].lower()
    algo_hashrate = algo["hashrate(H/second) "]
    algo_power_consumption = algo["power_consumption(W)"]
    algo_df = coin_df[coin_df["algorithm"] == algo_name]

    temp_df = algo_df

    # Raw profit for this algo
    # Make profit columns
    temp_df["profit_hourly"] = algo_hashrate * temp_df["profit/hash/hour"]
    temp_df["profit_daily"] = algo_hashrate * temp_df["profit/hash/hour"] * 24
    temp_df["profit_monthly"] = algo_hashrate * temp_df["profit/hash/hour"] * 24 * 30
    temp_df = temp_df[
        ["coin", "name", "type", "algorithm", "network_hashrate", "difficulty", "reward_block", "reward_unit",
         "profit_hourly", "profit_daily", "profit_monthly"]]

    # Make electricity cost columns
    hourly_electricity_cost = (algo_power_consumption / 1000) * get_electricity_data(country)
    daily_electricity_cost = hourly_electricity_cost * 24
    monthly_electricity_cost = daily_electricity_cost * 30
    temp_df["hourly_electricity_cost"] = hourly_electricity_cost
    temp_df["daily_electricity_cost"] = daily_electricity_cost
    temp_df["monthly_electricity_cost"] = monthly_electricity_cost

    # Final profit columns
    temp_df["final_profit_hourly"] = temp_df["profit_hourly"] - temp_df["hourly_electricity_cost"]
    temp_df["final_profit_daily"] = temp_df["profit_daily"] - temp_df["daily_electricity_cost"]
    temp_df["final_profit_monthly"] = temp_df["profit_monthly"] - temp_df["monthly_electricity_cost"]

    return temp_df


# In[24]:
def make_country_list():
    with open("resources/us_states.txt") as r:
        data = r.readlines()
        data = list(map(lambda x: x[:-1], data))
        data.append("Finland")
        return data


def main(country):
    # Get all the databases needed for profit calculation without shipping/taxes
    machine_df = get_machines_data()
    time = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
    currency_conversion_rate()

    # Loop through each machine on the list and create dataframe for each algorithm for each machine with profit information
    for x in range(machine_df.shape[0]):
        name = f'{machine_df["Manufacturer"].iloc[x]}_{machine_df["Model"].iloc[x]}'
        # size_cubic_inch = (machine_df["Size(mm)"].iloc[x]["x"] * machine_df["Size(mm)"].iloc[x]["y"] * machine_df["Size(mm)"].iloc[x]["z"]) / 16390
        # weight = machine_df["Weight(g)"].iloc[x] / 453.6
        algorithms = machine_df["Algorithm_and_power"].iloc[x]

        total_df = pd.DataFrame()
        # Loop through each algorithm found for machine and create dataframes
        for algo in algorithms:
            temp_df = dataframe_for_algo(algo, country)
            total_df = pd.concat([total_df, temp_df])

        # Checking if collection already exists for said machine --> if it does then update data and new time stamp
        # Else create new collection for new machine
        col = client["Asic_machine_profit"][country]
        sort = list({'_id': -1}.items())
        result = col.find(sort=sort, limit=1)

        if result is None:
            col.insert_one({"time": time, "machine_name": name, "data": total_df.to_dict(orient="records")})
        else:
            new_data = {"$set": {"time": time, "data": total_df.to_dict(orient="records")}}
            col.update_one({"machine_name": name}, new_data)


# In[25]:

if __name__ == '__main__':
    start_time = dt.datetime.now()

    print(f"[Program] Starting...")
    country_list = make_country_list()

    for x, country in enumerate(country_list):
        print(f"[Progress] {(x + 1)}/{len(country_list)} ----- {round(((x + 1) / len(country_list) * 100), 2)}%")
        print(f"[Algorithm] {country} in progress...")
        main(country)
        print(f"[Algorithm] {country} done")

    print(f"[RUNTIME] Total runtime: {dt.datetime.now() - start_time} seconds")
