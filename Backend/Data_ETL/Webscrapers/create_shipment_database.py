#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pymongo
import pandas as pd
import math
import WS_coolparcel_firefox as ws
import datetime as dt


# In[2]:


time = "2022-07-17T20_14_41"
client = pymongo.MongoClient()
db = client["Crypto-mining"]
col = db["ASICS-PoW"]


# In[3]:


data = col.find_one({"time": time})
df = pd.DataFrame(data["data"])
df


# In[4]:


df.iloc[0,3]


# In[5]:


x_list = []
y_list = []
z_list = []
for x in range(df.shape[0]):
    size = df.iloc[x, 3]
    if str(size) != "nan":
        x_list.append(size["x"])
        y_list.append(size["y"])
        z_list.append(size["z"])
    else:
        x_list.append(0)
        y_list.append(0)
        z_list.append(0)


# In[6]:


df["width"] = x_list
df["length"] = z_list
df["height"] = y_list


# In[7]:


df


# In[8]:


df["total_size"] = df["width"] * df["length"] * df["height"]


# In[9]:


df


# In[10]:


df.describe()


# cube mm to cube inch divide value by 16390
# g to lb for an approximate result, divide the mass value by 453.6

# In[11]:


mean_size = df.describe().iloc[1, 5] / 16390
mean_weigth = df.describe().iloc[1, 0] / 453.6
print(mean_size)
print(mean_weigth)


# In[12]:


size_dict = {
    "150%": [mean_size * 1.5, (mean_size * 1.5) ** (1. / 3.), (mean_weigth * 1.5)],
    "125%": [mean_size * 1.25, (mean_size * 1.25) ** (1. / 3.), (mean_weigth * 1.25)],
    "100%": [mean_size, mean_size ** (1. / 3.), (mean_weigth * 1.0)],
    "75%": [mean_size * 0.75, (mean_size * 0.75) ** (1. / 3.), (mean_weigth * 0.75)],
    "50%": [mean_size * 0.5, (mean_size * 0.5) ** (1. / 3.), (mean_weigth * 0.5)],
}


# array == cube inch, side inch, weight pound

# In[13]:


size_dict


# In[14]:


side = str(round(size_dict["150%"][1], 0))
weight = str(round(size_dict["150%"][2], 0))
print(side)
print(weight)


# In[15]:


def scrape_price(side:str, weight:str, from1:str, to1:str):
    addresses = ws.init(from1, to1, {"weight": weight, "length": side, "width": side, "height": side})
    if len(addresses) != 0:
        return int(addresses[0]["cost"][1:])
    else:
        return False


# In[15]:


from_countries = [
    "China",
    "Germany",
    "Texas"
]

to_countries = [
    "Finland",
    "New York"
]


# In[16]:

start_time = dt.datetime.now()

shipment_data = []

for k, v in size_dict.items():
    for from_country in from_countries:
        for to_country in to_countries:
            ship_data = {"class": k, "size(inch cube)": v[0], "weight (lb)": v[2], "from": from_country}
            ship_data["to"] = to_country
            
            # Get side and weight
            side = str(round(v[1], 0))
            weight = str(round(v[2], 0))
            price = scrape_price(side, weight, from_country, to_country)
            ship_data["price ($)"] = price

            print(ship_data)
            shipment_data.append(ship_data)


print(f"[RUNTIME] {dt.datetime.now() - start_time} seconds")
# In[ ]:


print(shipment_data)

ws.stop_driver()

db = client["Shipments"]
col = db["international_routes"]

df1 = pd.DataFrame(shipment_data)

col.insert_one({"time": dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S"), "data": df1.to_dict(orient="records")})

