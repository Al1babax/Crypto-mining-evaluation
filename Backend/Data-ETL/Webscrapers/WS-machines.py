from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
import json
import re

# Main function for webscraping machines
def main():
    dict_of_machines={}
    counter=1
    for machine in link_of_machines:
        dict_of_one_machine_spec=get_specs_from_website_table(url+machine[1:])
        dict_of_machines['machine '+str(counter)]=dict_of_one_machine_spec
        dict_of_one_machine_spec['coins']=get_minable_coin_of_machine(url+machine[1:])
        dict_of_one_machine_spec['available stores']=get_market_prices(url+machine[1:])
        counter+=1
    create_json_file('fina_result.json',dict_of_machines)

# Selenium initliazing 
def webscraper_id():
    DRIVER_PATH=r'C:\Users\user\Desktop\AllFolders\Coding2.0\CryptoMiningProject\packages\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)  
    return driver


url='https://www.asicminervalue.com/'


#getting all machines link from the url page
def get_all_links_of_website_pages(url):
    source_code=requests.get(url)
    soup=BeautifulSoup(source_code.text,'lxml')
    links_from_website=soup.find_all('a')
    link_of_machine_page=[]
    for link in links_from_website:
        if 'miner' in link.get('href'):
            link_of_machine_page.append(link.get('href'))
    return link_of_machine_page

link_of_machines=get_all_links_of_website_pages(url)

#Scrapping the spec from the website 
def get_specs_from_website_table(url):
    source_code=requests.get(url)
    soup=BeautifulSoup(source_code.text,'lxml')
    locate_div=soup.find('div',class_='col-sm-8')
    locate_table_from_div=locate_div.find('table',class_='table table-striped')
    specs=locate_table_from_div.find_all('tr')
    specs_label=locate_table_from_div.find_all('th')
    list_of_specs=[]
    list_of_specs_label=[]
    for spec in specs:
        spec_name=spec.find('td').text
        list_of_specs.append(spec_name)
    for label in specs_label:
        list_of_specs_label.append(label.text)
    dict_of_machines_spec={}
    for ele in range(0,len(list_of_specs_label)):
        dict_of_machines_spec[list_of_specs_label[ele]]=list_of_specs[ele]
    return dict_of_machines_spec


# create a json file for prototype
def create_json_file(destination,dict):
    with open(destination,'w+') as f:
        json.dump(dict,f,indent=10)



# get minable coins for one machine
def get_minable_coin_of_machine(url):
    source_code=requests.get(url)
    soup=BeautifulSoup(source_code.text,'lxml')
    locate_div=soup.find_all('img',class_='img-responsive')
    list_of_minable_coins=[]
    for i in locate_div:
            coin=i.get('title')
            if coin is not None:
                list_of_minable_coins.append(remove_b_tags(coin))
    return list_of_minable_coins
    
# remove <b> from one coins data
def remove_b_tags(string):
    left=re.search('<b>',string)
    left_index=left.span()[1]
    right=re.search('</b>',string)
    right_index=right.span()[0]
    return string[left_index:right_index]

# get market price and stores for one machine
def get_market_prices(url):
    driver=webscraper_id()
    driver.get(url)

    nb_of_stores=driver.find_elements(By.XPATH,'/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr')

    list_of_markets=[]

    for counter in range(0,len(nb_of_stores)):
        name=driver.find_element(By.XPATH,'/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(counter+1)+']/td[2]/b/a')
        country=driver.find_element(By.XPATH,'/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(counter+1)+']/td[2]/span/img').get_attribute("data-original-title")
        price=driver.find_element(By.XPATH,'/html/body/div[2]/div[7]/div/div/div/div[2]/div/table/tbody/tr['+str(counter+1)+']/td[3]/b')
        dict_of_stores={'name':name.text,'country':country,'price':price.text}
        list_of_markets.append(dict_of_stores)
    driver.quit()
    return list_of_markets


#calling the main function
main()