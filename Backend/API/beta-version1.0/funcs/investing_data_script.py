#!/usr/bin/env python
# coding: utf-8

# In[74]:


import pandas as pd
import pymongo
client = pymongo.MongoClient()


# In[75]:


def get_dataframes():
    # Profit dataframe without any costs
    result_list = list(client['Asic_machine_profit']['Finland'].find({}))
    full_df = pd.DataFrame()

    for result in result_list:
        temp_df = pd.DataFrame(result["data"])
        temp_df["machine_name"] = result["machine_name"]
        full_df = pd.concat([full_df, temp_df])

    # Shipment dataframe
    sort=list({'_id': -1}.items())
    limit=1
    result = client['Shipments']['international_routes'].find(
        sort=sort,
        limit=limit
    )
    shipment_df = pd.DataFrame(result[0]["data"])

    # Machine and market info dataframes
    sort=list({'_id': -1}.items())
    limit=1
    result = client['Crypto-mining']['ASICS-PoW-final'].find(
        sort=sort,
        limit=limit
    )
    market_df = pd.DataFrame(result[0]["data"])
    market_df["machine_name"] = market_df["Manufacturer"] + " " + market_df["Model"]
    machine_info_df = market_df
    market_df = market_df[["machine_name",'available_stores']]

    # returns all the dataframes
    return full_df, shipment_df, machine_info_df, market_df


# ## Do two different dataframes one for us one for Finland to determine the cheapest machine for each location --> US calculate location is New York

# In[76]:


def make_destination_market_dataframes(market_df):
    fin_market_df = market_df
    fin_market_df = fin_market_df[~fin_market_df["available_stores"].isna()]
    us_market_df = market_df
    us_market_df = us_market_df[~us_market_df["available_stores"].isna()]
    return fin_market_df, us_market_df


# In[77]:


def create_country_mapping(fin_market_df):
    # This can be run if new countries are needed to be mapped
    """countries = []
    for x in range(fin_market_df.shape[0]):
        machine_market_data = fin_market_df.iloc[x, 1]
        for market in machine_market_data:
            # print(market)
            countries.append(market["country"])
            # print()

    inv_countries = list(set(countries))
    country_mapping = {
        "EU": [inv_countries[1], inv_countries[7], inv_countries[5]],
        "US": [inv_countries[6], inv_countries[0]],
        "ASIA": [inv_countries[2], inv_countries[3], inv_countries[8], inv_countries[4]]
    }"""
    country_mapping = {'EU': ['Italia', 'United Kingdom', 'Germany'],
     'US': ['United States', 'Canada'],
     'ASIA': ['Israel', 'Hong Kong', 'China', 'Honk Kong']}
    return country_mapping


# ## cube mm to cube inch divide value by 16390
# ## g to lb for an approximate result, divide the mass value by 453.6

# In[78]:


def modify_machine_info_df(machine_info_df):
    x_list = []
    y_list = []
    z_list = []
    for x in range(machine_info_df.shape[0]):
        size = machine_info_df.iloc[x, 3]
        if str(size) != "nan":
            x_list.append(size["x"])
            y_list.append(size["y"])
            z_list.append(size["z"])
        else:
            x_list.append(0)
            y_list.append(0)
            z_list.append(0)

    machine_info_df["width"] = x_list
    machine_info_df["length"] = z_list
    machine_info_df["height"] = y_list
    machine_info_df["total_size"] = machine_info_df["width"] * machine_info_df["length"] * machine_info_df["height"]

    machine_info_df["cube_inch"] = machine_info_df["total_size"] / 16390
    machine_info_df["lb"] = machine_info_df["Weight(g)"] / 453.6
    return machine_info_df


# In[79]:


def check_machine_category(machine_name, machine_info_df): # Checks what is category of size the machines is closest to calculate shipment cost
    machine_df = machine_info_df[(machine_info_df["machine_name"] == machine_name)]
    custom_var_number = (machine_df["cube_inch"] * machine_df["lb"]).iloc[0]
    category_custom_var_numbers = [35002, 24307, 15556, 8750, 3889]
    difference_list = []

    for index, number in enumerate(category_custom_var_numbers):
        difference = abs(number - custom_var_number)
        difference_list.append(difference)

    # print(difference_list)
    smallest_numbers_index = difference_list.index(min(difference_list))
    category_dict = {
        0: "150%",
        1: "125%",
        2: "100%",
        3: "75%",
        4: "50%"
    }
    return category_dict[smallest_numbers_index]


# ![](resources/images/blJg20D.jpg)

# ## This function above is for choose_best_market function to choose what is the best machine --> For now I will just use what is the cheapest machine available

# In[80]:


def choose_best_market(market_list:list, to_country):
    """
    Best machine market is chosen based on real price which includes shipping price --> There needs to be custom weights on markets lists with saying that item will be in stock within certain time --> Best way to calculate these weights would be to use coin profit prediction algorithms to determine how much profit will said machine lose each month and use that information to make weights --> but because I don't have that information yet I need to make my own custom weights. Let's say that machine is outdate in 3years to 0 profit and with average ROI of 1.5 years we can access how much they lose profit per one month. Let's also assume mining profit per month loss is linear -->
    Total profit: machine_price * 2
    One month of 3 years(one month profit loss): 1/(12*2)
    At 1.5year machine making 50% of original profit
    :param market_list:
    :return:
    """
    stock_name_dict = {'In stock',
     'In stock(10 \\ndays\\n)',
     'In stock(12 \\ndays\\n)',
     'In stock(15 \\ndays\\n)',
     'In stock(2 \\ndays\\n)',
     'In stock(3 \\ndays\\n)',
     'In stock(30 \\ndays\\n)',
     'In stock(5 \\ndays\\n)',
     'In stock(7 \\ndays\\n)',
     'Out of stock',
     'Pre-order(Aug\\xa02022)',
     'Pre-order(Jul\\xa02022)',
     'Pre-order(Jun\\xa02022)',
     'Pre-order(May\\xa02022)',
     'Pre-order(Oct\\xa02022)',
     'Used'}

    # Adding import taxes here
    """
    For Finland it is 24% outside of eu
    For US it is 2% outside US and 25% if from China
    """
    if to_country == "Finland":
        for market in market_list:
            if market["continent"] != "EU" or market["country"] == "United Kingdom":
                market["tax_added_price"] = market["real_price"] * 1.24
            else:
                market["tax_added_price"] = market["real_price"]
    elif to_country == "New York":
        for market in market_list:
            if market["continent"] != "US":
                market["tax_added_price"] = market["real_price"] * 1.02
            elif market["country"] in ["China", "Hong Kong", "Honk Kong"]:
                market["tax_added_price"] = market["real_price"] * 1.25
            else:
                market["tax_added_price"] = market["real_price"]

    # Sorting list
    market_list.sort(key = lambda x: x["tax_added_price"])

    """for market in market_list:
        print(market)
    print()"""
    for market in market_list:
        if market["stock"] != "Used" or market["stock"] != "Out of stock":
            return market


# In[81]:


def format_price(price:str):
    price = price[1:]
    price = price.replace(",", "").split(".")[0]
    return int(price)


# In[82]:


def calculate_shipment(data, shipment_df:pd.DataFrame, to_country):
    if data["isFreeShipping"] is True:
        return 0
    # print(to_country)
    # print(data["size_category"])

    ship_df = shipment_df[(shipment_df["to"] == to_country) & (shipment_df["class"] == data["size_category"])]
    if data["continent"] == "EU":
        ship_df = ship_df[ship_df["from"] == "Germany"]
    elif data["continent"] == "US":
        ship_df = ship_df[ship_df["from"] == "Texas"]
    elif data["continent"] == "ASIA":
        ship_df = ship_df[ship_df["from"] == "China"]
    # print(ship_df)
    return ship_df.iloc[0, 5]


# In[83]:


def include_shipping_taxes(country1, country_market_df, country_mapping, machine_info_df, shipment_df):
    country_modified_market = []

    for x in range(country_market_df.shape[0]):
        machine_market_data = country_market_df.iloc[x, 1]
        machine_name = country_market_df.iloc[x, 0]
        all_markets_list = []

        for market in machine_market_data:
            country = market["country"]
            temp_dict = {
                "store_name": market["store_name"],
                "non_ship_price": format_price(market["price"]),    # Formatting price
                "country": country,
                "stock": market["stock"],
                "isFreeShipping": market["isFreeShipping"]
            }
            machine_size_category = check_machine_category(machine_name, machine_info_df)
            temp_dict["size_category"] = machine_size_category
            if country in country_mapping["EU"]:
                temp_dict["continent"] = "EU"
            elif country in country_mapping["US"]:
                temp_dict["continent"] = "US"
            elif country in country_mapping["ASIA"]:
                temp_dict["continent"] = "ASIA"

            # print(temp_dict)
            shipment_cost = calculate_shipment(temp_dict,shipment_df, country1)
            # print(temp_dict)
            temp_dict["shipment_cost"] = shipment_cost
            temp_dict["real_price"] = float(temp_dict["non_ship_price"]) + float(temp_dict["shipment_cost"])
            # print(temp_dict)
            # print()
            if temp_dict["stock"] == "In stock":
                all_markets_list.append(temp_dict)

        cheapest_market = choose_best_market(all_markets_list, country1)
        machine_market = {"machine_name": machine_name, "cheapest_market": cheapest_market, "cheapest_price": cheapest_market["real_price"] if cheapest_market is not None else 0}
        country_modified_market.append(machine_market)
        # print(cheapest_market)
        # print()

    return pd.DataFrame(country_modified_market)


# In[84]:


def main():
    # Getting all the dataframes
    full_df, shipment_df, machine_info_df, market_df = get_dataframes()

    # Split into two markets
    fin_market_df, us_market_df = make_destination_market_dataframes(market_df)

    # Make countries mapped to continents
    country_mapping = create_country_mapping(fin_market_df)

    # Modify machine measurements to imperial units
    machine_info_df = modify_machine_info_df(machine_info_df)

    # Market dataframes with shipments and taxes included
    fin_modified_market_df = include_shipping_taxes("Finland", fin_market_df, country_mapping, machine_info_df, shipment_df)
    us_modified_market_df = include_shipping_taxes("New York", us_market_df, country_mapping, machine_info_df, shipment_df)

    return fin_modified_market_df, us_modified_market_df


# In[85]:


fin_df, us_df = main()


# In[86]:


print(fin_df)


# In[90]:


print(us_df)


# In[87]:




