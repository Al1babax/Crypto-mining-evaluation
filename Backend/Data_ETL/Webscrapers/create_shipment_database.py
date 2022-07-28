import pymongo
import pandas as pd
import WS_coolparcel_firefox as ws
import datetime as dt

client = pymongo.MongoClient()


def get_data(time1):
    db = client["Crypto-mining"]
    col = db["ASICS-PoW-final"]

    data = col.find_one({"time": time1})
    df = pd.DataFrame(data["data"])

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

    df["width"] = x_list
    df["length"] = z_list
    df["height"] = y_list
    df["total_size"] = df["width"] * df["length"] * df["height"]

    return df


def make_size_dict(df):
    mean_size = df.describe().iloc[1, 5] / 16390
    mean_weigth = df.describe().iloc[1, 0] / 453.6
    size_dict = {
        "150%": [mean_size * 1.5, (mean_size * 1.5) ** (1. / 3.), (mean_weigth * 1.5)],
        "125%": [mean_size * 1.25, (mean_size * 1.25) ** (1. / 3.), (mean_weigth * 1.25)],
        "100%": [mean_size, mean_size ** (1. / 3.), (mean_weigth * 1.0)],
        "75%": [mean_size * 0.75, (mean_size * 0.75) ** (1. / 3.), (mean_weigth * 0.75)],
        "50%": [mean_size * 0.5, (mean_size * 0.5) ** (1. / 3.), (mean_weigth * 0.5)],
    }
    return size_dict


def scrape_price(side: str, weight: str, from1: str, to1: str):
    addresses = ws.init(from1, to1, {"weight": weight, "length": side, "width": side, "height": side})
    if len(addresses) != 0:
        return int(addresses[0]["cost"][1:])
    else:
        return False


def save_mongodb(shipment_data):
    db = client["Shipments"]
    col = db["international_routes"]

    df1 = pd.DataFrame(shipment_data)

    col.insert_one({"time": dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S"), "data": df1.to_dict(orient="records")})


def main(time1):
    df = get_data(time1)
    size_dict = make_size_dict(df)
    # side = str(round(size_dict["150%"][1], 0))
    # weight = str(round(size_dict["150%"][2], 0))
    from_countries = [
        "China",
        "Germany",
        "Texas"
    ]
    to_countries = [
        "Finland",
        "New York"
    ]

    start_time = dt.datetime.now()
    shipment_data = []

    amount_of_iterations = len(size_dict.keys()) * len(from_countries) * len(to_countries)
    current_iteration = 0

    for k, v in size_dict.items():
        for from_country in from_countries:
            for to_country in to_countries:
                current_iteration += 1
                print(f"[Progress] {current_iteration}/{amount_of_iterations}")
                ship_data = {"class": k, "size(inch cube)": v[0], "weight (lb)": v[2], "from": from_country,
                             "to": to_country}

                # Get side and weight
                side = str(round(v[1], 0))
                weight = str(round(v[2], 0))
                price = scrape_price(side, weight, from_country, to_country)
                ship_data["price ($)"] = price

                print(ship_data)
                shipment_data.append(ship_data)

    print(f"[RUNTIME] {dt.datetime.now() - start_time} seconds")
    print(shipment_data)
    ws.stop_driver()
    save_mongodb(shipment_data)


if __name__ == '__main__':
    time2 = "2022-07-28T10_27_10"
    main(time2)
