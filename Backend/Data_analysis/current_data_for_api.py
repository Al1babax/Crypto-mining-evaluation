#!/usr/bin/env python
# coding: utf-8

# In[102]:


import pandas as pd
import pymongo
import datetime as dt

client = pymongo.MongoClient()
time = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")


# In[103]:


def get_data(col_name):
    # Profit data
    col = client["Asic_machine_profit"][col_name]
    docs = col.find({})

    total_df = pd.DataFrame()
    for doc in docs:
        if len(doc["data"]) != 0:
            df = pd.DataFrame(doc["data"])
            machine_name = doc["machine_name"]
            df = clean_df(df, machine_name)
            total_df = pd.concat([total_df, df])
    return total_df


# In[104]:


def clean_df(df, machine_name):
    df = df.drop(["network_hashrate", "difficulty", "reward_block", "profit_hourly", "profit_daily", "profit_monthly",
                  "hourly_electricity_cost", "daily_electricity_cost", "monthly_electricity_cost"], axis=1)
    df = df[df["type"] == "coin"]
    df["machine_name"] = machine_name
    first_column = df.pop("machine_name")
    df.insert(0, "machine_name", first_column)
    return df


# In[105]:


def round_data(df):
    df["final_profit_hourly"] = df["final_profit_hourly"].apply(lambda x: round(x, 2))
    df["final_profit_daily"] = df["final_profit_daily"].apply(lambda x: round(x, 2))
    df["final_profit_monthly"] = df["final_profit_monthly"].apply(lambda x: round(x, 2))
    return df


# In[106]:


def save_to_mongo(df, country):
    col = client["API_data"]["current_profit"]
    result = col.find({"country/state": country})
    col.insert_one({"time": time, "country/state": country, "data": df.to_dict(orient="index")})
    if not list(result):
        col.insert_one({"time": time, "country/state": country, "data": df.to_dict(orient="index")})
    else:
        new_data = {"$set": {"time": time, "data": df.to_dict(orient="index")}}
        col.update_one({"country/state": country}, new_data)


# In[107]:


def main(country, coin=None, pool=None, algorithm=None,
         machine_name= None):
    all_data_df = pd.DataFrame()

    # Check country
    if country is None:
        for col in client["Asic_machine_profit"].list_collection_names():
            all_data_df = pd.concat([all_data_df, get_data(col)])
    else:
        all_data_df = get_data(country)
        """for country in countries:
            all_data_df = pd.concat([all_data_df, get_data(country)])"""

    # Check coin type
    if coin is not None:
        all_data_df = all_data_df[all_data_df["coin"] == coin.upper()]
        """for coin in coins:
            all_data_df = all_data_df[all_data_df["coin"] == coin.upper()]"""

    # Check pools
    # Passing pools for now

    # Check algo
    if algorithm is not None:
        all_data_df = all_data_df[all_data_df["algorithm"] == algorithm.lower()]
        """for algo in algorithms:
            all_data_df = all_data_df[all_data_df["algorithm"] == algo.lower()]"""

    # Check machine names
    if machine_name is not None:
        all_data_df = all_data_df[all_data_df["coin"] == machine_name]
        """for machine in machine_names:
            all_data_df = all_data_df[all_data_df["coin"] == machine]"""


    all_data_df["index"] = [str(x) for x in range(all_data_df.shape[0])]
    all_data_df = all_data_df.set_index("index")

    # Round numbers for api
    all_data_df = round_data(all_data_df)
    # save to mongo
    save_to_mongo(all_data_df, country)


# In[108]:

if __name__ == '__main__':
    for country in client["Asic_machine_profit"].list_collection_names():
        main(country)


# In[108]:




