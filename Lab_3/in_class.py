import requests
from bs4 import BeautifulSoup
import re
import os
import json

from homework import *

def scanPages(url: str, init_num: int, page_num: int, urls: [], max_num_pages=None):
    response = requests.get(url)
    if response.status_code == 200:
        if max_num_pages != None:
            if page_num == init_num + max_num_pages:
                return urls
        
        parser = BeautifulSoup(response.content, features='lxml')
        parser.prettify()

        advertisements = set()
        links = parser.findAll('a', href=True)
        nextPageUrl = 'https://999.md' + findNextPage(url, links, page_num)

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
        if re.match(rf"{url}&page={page_num+1}", link['href']):
            return link['href']
    return ''


def main():
    site_url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page=10'
    list_of_urls = []
    
    p_n = 0
    i_n = 0
    if 'page' in site_url:
        p = re.split(r"&(page=[0-9]+)", site_url)[1]
        p_n = int(re.split(r"=", p)[1])
        i_n = p_n
    else:
        p_n = 1
        i_n = p_n
       
    scanPages(site_url, i_n, p_n, list_of_urls, max_num_pages=1)
    '''
    option = 'x'
    if os.path.exists('Lab_3/apartments.json'):
        option = 'w'

    apart_json = {}
    list_of_apartments = []
    for page_set in list_of_urls:
        for apartment_url in page_set:
            list_of_apartments.append(scanAdvertisement(apartment_url))

    apart_json['apartments'] = list_of_apartments

    with open('Lab_3/apartments.json', option) as apart:
        apart.write(json.dumps(apart_json, ensure_ascii=False, indent=4))
    '''

    option = 'x'
    if os.path.exists('Lab_3/links.txt'):
        option = 'w'

    with open('Lab_3/links.txt', option) as links:
        for url_set in list_of_urls:
            links.write(f'Page {i_n}\n')
            for url in url_set:
                links.write(url + '\n')
            links.write('\n\n\n')
            i_n += 1


if __name__ == '__main__':
    main()