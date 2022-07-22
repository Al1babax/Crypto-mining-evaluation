import requests
import multiprocessing

url = "http://84.250.90.224:8005/api/profit_data?country=Texas"


def run_test():
    for _ in range(20):
        response = requests.get(url)


if __name__ == '__main__':
    run_test()
    amount_of_processes = 1

    process_list = []

    for x in range(amount_of_processes):
        p = multiprocessing.Process(target=run_test)
        p.start()
        process_list.append(p)

    for process in process_list:
        process.join()
