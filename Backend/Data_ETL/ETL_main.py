"""
Runs all the web scrapers and all api collector scripts in order

DO NOT RUN UNTIL ALL SCRIPTS ARE WORKING AND TESTED
"""

# imports
import Webscrapers.WS_ASICsmachines as asics
import Webscrapers.WS_electricity as ele
import API_collectors.general_coin_data as coin
import datetime as dt
import subprocess
import logging

logging.basicConfig(level=logging.INFO, filename="logs/etl.log", filemode="a+", format="%(asctime)s - %(levelname)s - %(message)s")
# If the first script fails this time will be used
time2 = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")


def run_data_gathering():
    try:
        time = asics.main()
        logging.info("WS_ASICmachines  run successfully")
    except:
        logging.exception("WS_ASICmachines script failed")
        time = time2

    print("------------------------------------------------------")
    try:
        ele.main(time)
        logging.info("WS_electricity run successfully")
    except:
        logging.exception("WS_electricity script failed")

    print("------------------------------------------------------")
    try:
        coin.main(time)
        logging.info("general_coin_data run successfully")
    except:
        logging.exception("general_coin_data script failed")

    print("------------------------------------------------------")
    subprocess.call(["python3", "Data_ETL/Webscrapers/create_shipment_database.py", time])
    print("------------------------------------------------------")


def main():
    # Getting the starting time for data gathering from first script running --> that ensures that we can find all data
    # with same time
    run_data_gathering()

    # Automated tests
    # TODO automatic testing that scrapers are writing right data to database
    # TODO some kind of automatic logging that could be sent with email alert of something failing


if __name__ == "__main__":
    main()
