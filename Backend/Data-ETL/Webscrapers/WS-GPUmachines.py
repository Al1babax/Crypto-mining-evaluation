import requests
import json

url = "https://api.minerstat.com/v2/hardware"

#get response from api
def get_gpu_json_from_api(url):

    headers = {
        "X-RapidAPI-Key": "3f722add89msh3718a9d2814ba6dp19173ejsn643b1ceedfc0",
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    return response.text


# used to turn response from api to json object
def turn_py_object_to_json(obj):
    return json.loads(obj)

# create lists of gpu's adn remove certain unnecessary keys from the json object
def create_list_of_gpus():
    json_file=turn_py_object_to_json(get_gpu_json_from_api(url))
    list_of_gpus=[]
    for gpu in json_file:
        if gpu['type']=='gpu':
            try:
                gpu.pop('id')
                gpu.pop('url')
                gpu.pop('specs')
                gpu.pop('type')
            except:
                pass

            list_of_gpus.append(gpu)
    return list_of_gpus

#create a json file to store json object for testing

def create_json_file(destination, dict):
    with open(destination, 'w+') as f:
        json.dump(dict, f,indent=3)

#main function to create a json file of gpu's
def main():
    dict_of_gpu={}
    counter=1
    for gpu in create_list_of_gpus():
        dict_of_gpu['gpu'+str(counter)]=gpu
        counter+=1
    create_json_file('gpu-final.json',dict_of_gpu)

    
#calling the main function 
main()