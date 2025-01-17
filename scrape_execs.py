import requests
from bs4 import BeautifulSoup
import json

def get_execs(scrape_url):

    
    response=requests.get(scrape_url)
    soup=BeautifulSoup(response.content,features="html.parser")
    leaders=soup.find_all("span",attrs={'class':'exec-committee__name'})
    role=soup.find_all("span",attrs={'class':'exec-committee__function'})
    exec_dict = [{"name":leaders[i].text.strip(),"role": role[i].text.strip().split('\n')[0]} for i in range(len(leaders))]

    return exec_dict

def write_dict(dict):
    with open('./assets/execs.json', 'w', encoding ='utf8') as json_file:
        json.dump(dict,json_file)

def main():

    scrape_url="https://www.proximus.com/governance/executive-committee.html"
    
    execs=get_execs(scrape_url)

    write_dict(execs)


main()