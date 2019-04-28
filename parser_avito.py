# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re
import progressbar
import time
from xml.etree import ElementTree as ET
import pytesseract
from PIL import Image
import os


options = Options()
options.add_argument('--headless')
options.add_argument("disable-extensions")
options.add_argument("disable-infobars")
options.add_argument("test-type")
options.add_argument("ignore-certificate-errors")
options.add_argument("window-size=1050,800")


class Parser_avito:
    
    def __init__(self, url, browser=True, last_page=None, type_seller=str(0)):
        # Типы продавцов: 0 - все объявления, 1 - частные, 2 - организации
        self.url = url
        self.last_page = last_page
        # если URL с указанием уже с указанием типа продавца, то он таким и остается
        # есди нет, то добавляется стандартный "0" или значение переданне в параметр метода
        # if '?user=' not in self.url:
        #     self.url = self.url + '?user=' + type_seller
        try:
            if 'avito.ru' not in self.url:
                print('Неверный URL')
        except:
            print('Неверный URL')
        self.browser = browser
        if self.browser == True:
            self.browser = webdriver.Chrome(options=options)
            self.browser.set_page_load_timeout(11)
            try:
                self.browser.get(self.url)
            except :
                ActionChains(self.browser).send_keys(Keys.SHIFT).perform()
                print('Время зашрузки вышло')


    def _text_recognition(self):
        image = Image.open('avito.png')
        text = pytesseract.image_to_string(image).replace('—', '-')
        os.remove('avito.png')
        return text

    def _crop(self, location, size):
        image = Image.open('avito.png')
        x = location['x']
        y = location['y']
        width = size['width']
        height = size['height']
        image.crop((x, y, x+width, y+height)).save('avito.png')
        return self._text_recognition()

    def get_number(self):
        self.browser.find_element_by_xpath('//span[@class="item-phone-button-sub-text"]').click()
        time.sleep(3)
        self.browser.save_screenshot('avito.png')
        image = self.browser.find_element_by_xpath('//div[@class="item-phone-big-number js-item-phone-big-number"]//img')
        location = image.location
        size = image.size
        return self._crop(location, size)

    def get_request_to_avito(self, url=None):
        '''
        GET запрос к авито
        '''
        if url == None:
            return requests.get(self.url).text
        return requests.get(url).text

    def parsing_html_lxml(self):
        tree = html.fromstring(self.get_request_to_avito())
        return tree

    def parsing_html_BS4(self, url=None):
        if self.browser:
            if url != None:
                self.browser.set_page_load_timeout(11)
                try:
                    self.browser.get(url)
                except :
                    ActionChains(self.browser).send_keys(Keys.SHIFT).perform()
                    print('Время зашрузки вышло')
                self.soup = BeautifulSoup(self.browser.page_source, 'lxml')
                return self.soup
            self.browser.get(self.url)
            self.soup = BeautifulSoup(self.browser.page_source, 'lxml')
            return self.soup
        self.soup = BeautifulSoup(self.get_request_to_avito(url), 'lxml')
        return self.soup

    def get_last_page(self):
        if self.last_page == None:
            pages = self.parsing_html_BS4().findAll('a', class_='pagination-page')[-1]['href']
            last_page = re.search(r'p=\d{1,3}', pages).group().replace('p=', '')
            return last_page
        return self.last_page

    def findAll_links_to_ads(self, url=None):
        links = [link['href'] for link in self.parsing_html_BS4(url).findAll('a', class_='item-description-title-link')]
        return links

    def get_info_from_ads(self, url):

        soup = self.parsing_html_BS4(url)
        title = soup.find('span', class_='title-info-title-text').text
        if soup.find('div', class_='item-description-text'):
            description = soup.find('div', class_='item-description-text').text.strip()
        else:
            description = 'Описание не указано'
        category = 'Запчасти и аксессуары'
        if soup.find('span', class_='js-item-price'):
            price = soup.find('span', class_='js-item-price').text.strip()
        else:
            price = 'Договорная'
        currency = 'RUB'
        country = 'Россия'
        region = 'Пензенская область'
        city = 'Пенза'
        if soup.find('span', itemprop='streetAddress'):
            address = soup.find('span', itemprop='streetAddress').text.replace('Пенза,', '').strip()
        else:
            address = 'Пенза'
        if soup.find('a', title='Нажмите, чтобы перейти в профиль'):
            name = soup.find('a', title='Нажмите, чтобы перейти в профиль').text.strip()
        else:
            name = soup.find('div', class_='seller-info-name js-seller-info-name').text.strip()
        phone = self.get_number()
        item_params = [item.text.replace('\n', '').strip() for item in soup.findAll('li', class_='item-params-list-item')]
        if len(item_params) > 0:
            item_params = ','.join(item_params)
        else:
            item_params = u'Параметры товара не указаны'
        photo = []
        for img in soup.findAll('div', 'gallery gallery_state-clicked js-gallery'):
            img = img.findAll('img')
            for i in img:
                i = 'https:' + i['src'].replace('640x480', '1280x960')
                photo.append(i)
        photo = ', '.join(photo)
        link = url

        return [title, description, category, price, currency, country, region, city, address, name, phone, photo, link]


def create_xml_if_not_exists():
    if os.path.exists('test.xml'):
        pass
    else:
        with open('test.xml', 'w') as f:
            f.write('<root></root>')


def get_links_from_xml():
    with open('test.xml', 'r') as xml_file:
        soup = BeautifulSoup(xml_file, 'xml')
        links = soup.findAll('link')
        links =[l.text for l in links]
        return links


def main():
    create_xml_if_not_exists()
    p = Parser_avito('https://www.avito.ru/penza/zapchasti_i_aksessuary')
    last_page = int(p.get_last_page())
    for page in progressbar.progressbar(range(last_page)):
        for link in p.findAll_links_to_ads(p.url + '?p=' + str(page)):
            with open('test.xml', 'r') as xml_file:
                tree=ET.parse(xml_file)
                root=tree.getroot()
                if 'https://www.avito.ru' + link in get_links_from_xml():
                    pass
                else:
                    result = p.get_info_from_ads('https://www.avito.ru' + link)
                    time.sleep(1)
                    sroot_root = ET.Element("listing")
                    doc = ET.SubElement(sroot_root, "title").text = result[0]
                    doc = ET.SubElement(sroot_root, "description").text = result[1]
                    doc = ET.SubElement(sroot_root, "category").text = result[2]
                    doc = ET.SubElement(sroot_root, "price").text = result[3]
                    doc = ET.SubElement(sroot_root, "currency").text = result[4]
                    doc = ET.SubElement(sroot_root, "country").text = result[5]
                    doc = ET.SubElement(sroot_root, "region").text = result[6]
                    doc = ET.SubElement(sroot_root, "city").text = result[7]
                    doc = ET.SubElement(sroot_root, "address").text = result[8]
                    doc = ET.SubElement(sroot_root, "name").text = result[9]
                    doc = ET.SubElement(sroot_root, "phone").text = result[10]
                    doc = ET.SubElement(sroot_root, "photo").text = result[11]
                    doc = ET.SubElement(sroot_root, "link").text = result[12]

                    root.append(sroot_root)
                    tree = ET.ElementTree(root)
                    tree.write("test.xml", encoding="utf-8")


if __name__ == '__main__':
    main()

