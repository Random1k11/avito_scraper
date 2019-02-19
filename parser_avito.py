# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import csv


class Parser_avito:
    def __init__(self, url, last_page=None, type_seller=str(0)):
        # Типы продавцов: 0 - все объявления, 1 - частные, 2 - организации
        self.url = url
        # если URL с указанием уже с указанием типа продавца, то он таким и остается
        # есди нет, то добавляется стандартный "0" или значение переданне в параметр метода
        if '&user=' not in self.url:
            self.url = self.url + '&user=' + type_seller
        try:
            if 'avito.ru' not in self.url:
                print('Неверный URL')
        except:
            print('Неверный URL')

    def get_request_to_avito(self):
        '''
        GET запрос к авито
        '''
        self.r = requests.get(self.url)
        return self.r.text

    def parsing_html_lxml(self):
        tree = html.fromstring(self.get_request_to_avito())
        return tree

    def parsing_html_BS4(self):
        self.soup = BeautifulSoup(self.get_request_to_avito(), 'lxml')
        return self.soup

    def get_last_page(self):
        number_page = []  # список с номером страниц на 1-й странице
        last_number = []  # список с номером последней страницы
        HTML = self.parsing_html_lxml()
        for tag in HTML.findAll('div', class_="pagination-pages clearfix"):
            tag = tag.text.split()
            number_page.append(tag)
            if number_page[0][-1] == 'Последняя':
                click = browser.find_element_by_xpath(
                    '/html/body/div[2]/div[1]/div/div[7]/div[2]/div[3]/div/div[2]/a[4]')
                time.sleep(1)
                click.click()
                click = browser.find_element_by_xpath(
                    '/html/body/div[2]/div[1]/div/div[7]/div[2]/div[3]/div/div[2]/span')
                last_number.append(click.text)
            else:
                last_number.append(number_page[0][-1])
        print(number_page)




p = Parser_avito('https://www.avito.ru/ivanovo/avtomobili?radius=200').get_last_page()
print(p)