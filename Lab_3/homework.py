import requests
from bs4 import BeautifulSoup
import json

def scanAdvertisement(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        advertisement_data = {}

        parser = BeautifulSoup(response.content, features='lxml')
        parser.prettify()

        caracteristics = {}
        additional = {}

        div = parser.find('div', class_='adPage__content__features')
        list_of_caracteristics = div.findChild('ul')
        
        for child in list_of_caracteristics.findChildren('li'):
            values = child.findChildren('span')
            caracteristics[values[0].contents[0].strip()] = values[1].contents[0].strip()

        details_parser = BeautifulSoup(str(div), features='lxml')
        headers = details_parser.find_all('h2')
        advertisement_data[headers[0].contents[0]] = caracteristics
        advertisement_data[headers[1].contents[0]] = additional
        
    else:
        print(f"Request failed: {response.status_code}")

    return json.dumps(advertisement_data, ensure_ascii=False)


def main():
    site_url = 'https://999.md/ro/83487066'
    json_data = scanAdvertisement(site_url)
    print(json_data)

main()