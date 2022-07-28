import subprocess
import datetime as dt


def main():
    subprocess.call(["python", "Data_ETL/ETL_main.py"], shell=True)
    subprocess.call(["python", "Data_analysis/DS_main.py"], shell=True)


if __name__ == "__main__":
    start_time = dt.datetime.now()
    print("-----------------------------------------------------")
    print(f"Updating databases started at {start_time}")
    print("-----------------------------------------------------")
    main()
    end_time = dt.datetime.now()
    print("----------------------------------------------------")
    print(f"Total time for running all scripts {end_time - start_time}")
    print("----------------------------------------------------")
