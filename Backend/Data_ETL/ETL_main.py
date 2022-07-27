"""
Runs all the web scrapers and all api collector scripts in order

DO NOT RUN UNTIL ALL SCRIPTS ARE WORKING AND TESTED
"""

# imports
import Webscrapers.WS_ASICsmachines as asics
import Webscrapers.WS_electricity as ele
import API_collectors.general_coin_data as coin
import datetime as dt

# If the first script fails this time will be used
time2 = dt.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")


def run_data_gathering():
    try:
        time = asics.main()
    except:
        message = "Something went wrong with WS_ASICsmachines script"
        time = time2
    print("------------------------------------------------------")
    try:
        ele.main(time)
    except:
        message = "Something went wrong with WS_electricity script"
    print("------------------------------------------------------")
    try:
        coin.main(time)
    except:
        message = "Something went wrong with general_coin_data script"
    print("------------------------------------------------------")


def main():
    # Getting the starting time for data gathering from first script running --> that ensures that we can find all data
    # with same time
    run_data_gathering()

    # Data processing
    pass
    # Automated tests
    # TODO automatic testing that scrapers are writing right data to database
    # TODO some kind of automatic logging that could be sent with email alert of something failing


if __name__ == '__main__':
    main()
