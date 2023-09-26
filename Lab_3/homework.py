import requests
from bs4 import BeautifulSoup
import json

def scanAdvertisement(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        advertisement_data = {}

        parser = BeautifulSoup(response.content, features='lxml')
        parser.prettify()

        links = parser.find_all('div', class_='adPage__content__features__col')
        general_info = {}
        particularities = {}

        details_parser = BeautifulSoup(str(links), features='lxml')
        for header in details_parser.find_all('h2'):
            advertisement_data[header.contents[0]] = {}
    else:
        print(f"Request failed: {response.status_code}")

    return json.dumps(advertisement_data, ensure_ascii=False)


def main():
    site_url = 'https://999.md/ro/84284036'
    json_data = scanAdvertisement(site_url)
    print(json_data)

main()