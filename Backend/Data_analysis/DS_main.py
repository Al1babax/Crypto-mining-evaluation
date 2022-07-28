"""
Runs all the data cleaning and preparing for api
"""
import current_machine_profit
import investing_data_script
import investing_data_for_api


def main():
    current_machine_profit.init()
    investing_data_script.main()
    investing_data_for_api.main()


if __name__ == '__main__':
    main()
