#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import pymongo
import datetime as dt


# In[2]:


client = pymongo.MongoClient()
time1 = dt.datetime.now()
current_time = time1.strftime("%Y-%m-%dT%H_%M_%S")


# In[3]:


def api_coins():
    # API request
    result = requests.get("https://api.minerstat.com/v2/coins")
    result_json = result.json()

    # Json to dataframe and remove -1 also change some values to floats
    df = pd.DataFrame(result_json)
    df = df.replace(-1, 0)
    df["difficulty"] = df["difficulty"].apply(lambda x: float(x))
    df["profit/hash/hour"] = df["reward"] * df["price"]
    return df


# In[4]:


def write_database(df):
    db = client["Coin-Data"]
    col = db["Current_coin"]
    col.insert_one({"date": current_time, "data":df.to_dict(orient="records")})


# In[5]:


def main():
    start_time = dt.datetime.now()
    df = api_coins()
    write_database(df)
    print(f"Runtime: {dt.datetime.now() - start_time} seconds")


# In[6]:


if __name__ == '__main__':
    main()

