import pymongo
import pandas as pd

client = pymongo.MongoClient()


def make_json(df: pd.DataFrame):
    return df.to_dict()


async def main(country=None, coin=None, pool=None, algorithm=None,
         machine_name=None):
    if country in client["Asic_machine_profit"].list_collection_names():
        col = client["API_data"]["current_profit"]
        doc = col.find_one({"country/state": country})
        all_data_df = pd.DataFrame(doc["data"]).T

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
