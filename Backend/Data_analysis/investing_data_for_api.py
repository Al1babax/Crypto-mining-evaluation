#!/usr/bin/env python
# coding: utf-8

# In[128]:


import pandas as pd
import pymongo
import datetime as dt

# In[129]:


client = pymongo.MongoClient('localhost', 27017)
time = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")


# In[130]:


def clean_df(df, machine_name):
    df = df.drop(["network_hashrate", "difficulty", "reward_block", "profit_hourly", "profit_daily", "profit_monthly",
                  "hourly_electricity_cost", "daily_electricity_cost", "monthly_electricity_cost"], axis=1)
    df = df[df["type"] == "coin"]
    df["machine_name"] = machine_name
    first_column = df.pop("machine_name")
    df.insert(0, "machine_name", first_column)
    return df


# In[131]:


def get_data(col_name):
    # Profit data
    col = client["Asic_machine_profit_full"][col_name]
    docs = col.find({})

    total_df = pd.DataFrame()
    for doc in docs:
        if len(doc["data"]) != 0:
            df = pd.DataFrame(doc["data"])
            machine_name = doc["machine_name"]
            df = clean_df(df, machine_name)
            total_df = pd.concat([total_df, df])
    return total_df


# In[132]:


def save_to_mongo(df, country):
    col = client["API_data"]["invest_profit"]
    result = col.find({"country/state": country})
    if not list(result):
        col.insert_one({"time": time, "country/state": country, "data": df.to_dict(orient="records")})
    else:
        new_data = {"$set": {"time": time, "data": df.to_dict(orient="records")}}
        col.update_one({"country/state": country}, new_data)


# In[133]:


def main():
    print("Updating api masterdata started...")
    start_time = dt.datetime.now()
    for col in client["Asic_machine_profit_full"].list_collection_names():
        df = get_data(col)

        df["final_profit_hourly"] = df["final_profit_hourly"].apply(lambda x: float(x.replace(",", ".")))
        df["final_profit_daily"] = df["final_profit_daily"].apply(lambda x: float(x.replace(",", ".")))
        df["final_profit_monthly"] = df["final_profit_monthly"].apply(lambda x: float(x.replace(",", ".")))
        df["total_profit"] = df["total_profit"].apply(lambda x: float(x.replace(",", ".")))
        df["profit_after_ROI"] = df["profit_after_ROI"].apply(lambda x: float(x.replace(",", ".")))

        df["final_profit_hourly"] = df["final_profit_hourly"].round(2)
        df["final_profit_daily"] = df["final_profit_daily"].round(2)
        df["final_profit_monthly"] = df["final_profit_monthly"].round(2)
        df["total_profit"] = df["total_profit"].round(2)
        df["profit_after_ROI"] = df["profit_after_ROI"].round(2)

        df["ROI_days"] = df["ROI_days"].apply(lambda x: "never" if x == "0" else x)

        df = df.reset_index()
        df = df.drop(["index"], axis=1)
        df = df.applymap(str)
        save_to_mongo(df, col)
        print(f"{col} done")

    print(f"Updating api masterdata finished in {dt.datetime.now() - start_time}")


if __name__ == '__main__':
    main()
