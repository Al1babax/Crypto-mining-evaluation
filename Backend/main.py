import subprocess
import os


def main():
    subprocess.call(["python", "Data_ETL/ETL_main.py"], shell=True)
    subprocess.call(["python", "Data_analysis/DS_main.py"], shell=True)


if __name__ == "__main__":
    main()
