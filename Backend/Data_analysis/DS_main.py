"""
Runs all the data cleaning and preparing for api
"""
import current_machine_profit
import investing_data_script
import investing_data_for_api
import logging

logging.basicConfig(level=logging.INFO, filename="logs/ds.log", filemode="a+", format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    try:
        current_machine_profit.init()
        logging.info("current_machine_profit run successfully")
    except:
        logging.exception("current_machine_profit script failed")

    try:
        investing_data_script.main()
        logging.info("investing_data_script run successfully")
    except:
        logging.exception("investing_data_script script failed")

    try:
        investing_data_for_api.main()
        logging.info("invest_data_for_api run successfully")
    except:
        logging.exception("invest_data_for_api script failed")


if __name__ == '__main__':
    main()
