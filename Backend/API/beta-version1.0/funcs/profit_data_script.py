import pymongo
import pandas as pd

client = pymongo.MongoClient()


def make_json(df: pd.DataFrame):
    return df.to_dict()


async def get_machine_names():
    col = client["API_data"]["invest_profit"]
    doc = col.find_one({"country/state": "Finland"})
    all_data_df = pd.DataFrame(doc["data"])
    return {
        "machine_names": all_data_df["machine_name"].unique().tolist()
    }


async def get_countries():
    return {
        "countries": client["Asic_machine_profit"].list_collection_names()
    }


async def get_algorithms():
    col = client["API_data"]["invest_profit"]
    doc = col.find_one({"country/state": "Finland"})
    all_data_df = pd.DataFrame(doc["data"])
    return {
        "algorithms": all_data_df["algorithm"].unique().tolist()
    }


async def get_coins():
    col = client["API_data"]["invest_profit"]
    doc = col.find_one({"country/state": "Finland"})
    all_data_df = pd.DataFrame(doc["data"])
    all_coins = all_data_df["coin"].unique().tolist()
    all_coin_names = all_data_df["name"].unique().tolist()
    result = {}
    for index, coin in enumerate(all_coins):
        temp_dict = {"coin": coin, "name": all_coin_names[index]}
        result[str(index)] = temp_dict
    return result


async def main(country=None, coin=None, pool=None, algorithm=None,
               machine_name=None):
    if country in client["Asic_machine_profit"].list_collection_names():
        col = client["API_data"]["invest_profit"]
        doc = col.find_one({"country/state": country})
        all_data_df = pd.DataFrame(doc["data"])

        # Check coin type
        if coin is not None:
            all_data_df = all_data_df[all_data_df["coin"] == coin.upper()]

        # Check pools
        # Passing pools for now

        # Check algo
        if algorithm is not None:
            all_data_df = all_data_df[all_data_df["algorithm"] == algorithm.lower()]

        # Check machine names
        if machine_name is not None:
            all_data_df = all_data_df[all_data_df["machine_name"] == machine_name]

        return make_json(all_data_df.T)

# Only for testing
# print(main("Finland"))
# print(get_machine_names())
