import requests
from bs4 import BeautifulSoup


def get_currency_ratio():
    url = "https://www.xe.com/currencyconverter/convert/?Amount=1&From=EUR&To=USD"

    response = requests.get(url)
    doc = BeautifulSoup(response.text, "html.parser")

    p_tags = doc.find_all(text=" US Dollars")
    ratio = p_tags[0].parent.text.split(" ")[0]

    ratio_dict = {"eur": 1, "us(dollar)": float(ratio)}
    return ratio_dict
