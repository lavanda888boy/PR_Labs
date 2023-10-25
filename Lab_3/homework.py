import requests
from bs4 import BeautifulSoup

def scanAdvertisement(url: str):
    print(f'Processing url: {url}')
    response = requests.get(url)
    if response.status_code == 200:
        advertisement_data = {}

        parser = BeautifulSoup(response.content, features='html.parser')
        parser.prettify()

        advertisement_data['url'] = url

        findDetails(parser, advertisement_data)
        findPrice(parser, advertisement_data)
        findAddress(parser, advertisement_data)
        findContacts(parser, advertisement_data)
    else:
        print(f"Request failed: {response.status_code}")

    return advertisement_data


def findDetails(parser, advertisement_data):
    caracteristics = {}
    additional = []

    div = parser.find('div', class_='adPage__content__features__col')
    list_of_caracteristics = div.findChild('ul')
    
    for child in list_of_caracteristics.findChildren('li'):
        values = child.findChildren('span')
        caracteristics[values[0].contents[0].strip()] = values[1].contents[0].strip()

    header = div.find('h2')
    advertisement_data[header.contents[0]] = caracteristics

    div = div.find_next_sibling()
    list_of_caracteristics = div.findChild('ul')
    
    if list_of_caracteristics != None:
        for child in list_of_caracteristics.findChildren('li'):
            values = child.findChild('span')
            additional.append(values.contents[0].strip())
            
        header = div.find('h2')
        advertisement_data[header.contents[0]] = additional


def findPrice(parser, advertisement_data):
    div = parser.find('div', class_='adPage__content__price-feature')
    header = div.find('div', class_='adPage__content__price-feature__title')
    values = div.findChild('li').findChildren('span')
    advertisement_data[header.contents[0].strip()[:-1]] = values[0].contents[0].strip() + ' ' + values[1].contents[0].strip()


def findAddress(parser, advertisement_data):
    div = parser.find('dl', class_='adPage__content__region')
    header = div.findChild('dt')
    header_value = header.contents[0].strip()[:-1]
    advertisement_data[header_value] = ''
    for item in div.findChildren('dd'):
        advertisement_data[header_value] += item.contents[0].strip()


def findContacts(parser, advertisement_data):
    div = parser.find('dl', class_='adPage__content__phone')
    header = div.findChild('dt')
    header_value = header.contents[0].strip()[:-1]

    if div.find('a') != None:
        advertisement_data[header_value] = div.find('a').get('href')