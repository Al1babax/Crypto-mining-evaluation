import subprocess
import datetime as dt
import os


def main():
    subprocess.call(["python3", "Data_ETL/ETL_main.py"])
    subprocess.call(["python3", "Data_analysis/DS_main.py"])


if __name__ == "__main__":
    start_time = dt.datetime.now()
    os.chdir("/home/default/Crypto-mining-evaluation/Backend")
    print("-----------------------------------------------------")
    print(f"Updating databases started at {start_time}")
    print("-----------------------------------------------------")
    main()
    end_time = dt.datetime.now()
    print("----------------------------------------------------")
    print(f"Total time for running all scripts {end_time - start_time}")
    print("----------------------------------------------------")
