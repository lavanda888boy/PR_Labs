from bs4 import BeautifulSoup
import requests
import re


def scanPages(url: str, init_num: int, page_num: int, urls: [], max_num_pages=None):
    response = requests.get(url)
    if response.status_code == 200:
        url = re.sub(r'&page=\d+', '', url)

        if max_num_pages != None:
            if page_num == init_num + max_num_pages:
                return urls
        
        parser = BeautifulSoup(response.content, features='lxml')
        parser.prettify()

        advertisements = set()
        links = parser.findAll('a', href=True)
        nextPageUrl = findNextPage(url, links, page_num)
        print(nextPageUrl)

        if nextPageUrl == '':
            return urls
        
        for link in links:
            if re.match(r"/ro/[0-9]+", link['href']) and link['href'] not in advertisements:
                advertisements.add('https://999.md' + link['href'])

        urls.append(advertisements)
        page_num += 1

        scanPages(nextPageUrl, init_num, page_num, urls, max_num_pages)
        
    else:
        print(f"Request failed: {response.status_code}")


def findNextPage(url: str, links, page_num: int):
    for link in links:
        if f'page={page_num+1}' in link['href']:
            return f'{url}&page={page_num+1}'
    return ''


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