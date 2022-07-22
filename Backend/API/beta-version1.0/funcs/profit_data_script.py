import pymongo
import pandas as pd

client = pymongo.MongoClient()


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


def clean_df(df, machine_name):
    df = df.drop(["network_hashrate", "difficulty", "reward_block", "profit_hourly", "profit_daily", "profit_monthly",
                  "hourly_electricity_cost", "daily_electricity_cost", "monthly_electricity_cost"], axis=1)
    df = df[df["type"] == "coin"]
    df["machine_name"] = machine_name
    first_column = df.pop("machine_name")
    df.insert(0, "machine_name", first_column)
    return df


def make_json(df: pd.DataFrame):
    return df.to_dict(orient="index")


def main(country=None, coin=None, pool=None, algorithm=None,
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

    # return all_data_df
    all_data_df.sort_values("final_profit_monthly", ascending=False, inplace=True)
    all_data_df["index"] = [x for x in range(all_data_df.shape[0])]
    all_data_df = all_data_df.set_index("index")
    return make_json(all_data_df)

# Only for testing
# print(main(countries=["Finland"]))
