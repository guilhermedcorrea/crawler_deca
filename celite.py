from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
from typing import Literal, List
import json
from itertools import chain
from openpyxl.workbook import Workbook
from datetime import datetime
from config import get_engine
from tabela import ImagensColetadas
from sqlalchemy import insert


options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")
options.add_argument('--disable-infobars')
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options, executable_path=r"D:\produtoshausz\chromedriver\chromedriver.exe")


def insert_produtos(*args, **kwargs):
    engine = get_engine()
    with engine.connect() as conn:

        result = conn.execute(
                insert(ImagensColetadas),
                [
                  {"nomeproduto":kwargs.get("nomeproduto"),"SKU":kwargs.get("SKU")
                  ,"ean":kwargs.get("ean"),"imagem":kwargs.get("imagem"),"urlcoleta":kwargs.get("urlcoleta"),"marca":kwargs.get("marca")
                  }
                ]
            )
    



urls = ["https://www.celite.com.br/produtos/piso-box?page=1"]


def scroll() -> None:
    driver.implicitly_wait(7)
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage

        time.sleep(3)
            
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True


def get_url_produto():
    listas = []
    while True:
        try:
            scroll()
            urlsprodutos = driver.find_elements(By.XPATH,
            '/html/body/div[1]/section/div/div/div/div/div[2]/section/div/div[2]/div/section[2]/div[1]/div[3]/div/div/div/div/div[1]/div[1]/div/a')
            for produtos in urlsprodutos:
                
                listas.append(produtos.get_attribute('href'))

        except Exception as e:
            scroll()
            try:
                urlsprodutos = driver.find_elements(By.XPATH
                ,'/html/body/div[1]/section/div/div/div/div/div[2]/section/div/div[2]/div/section[2]/div/div/div/div/div/div/div/div/div/a')

                for produtos in urlsprodutos:
                    listas.append(produtos.get_attribute('href'))
                print("error",e)
            except:
                pass
        try:
            driver.find_element(By.ID,'nextButtonTotalsSpan').click()
        except:
            break
    return listas

def get_urls():
    lista_urls = []
    driver.implicitly_wait(3)
    for url in urls:
        if re.search('[?page=]\d+',url):
            url = url.split("?page=")
            value = url[0] + '?page='
            for i in range(int(url[-1])):
                url_produto = value+f"{i}"
                driver.get(url_produto)
                urlproduto = get_url_produto()
                lista_urls.append(urlproduto)
        else:
            driver.get(url_produto)
            urlproduto = get_url_produto()
            lista_urls.append(urlproduto)
            
    return  lista_urls

def get_produtos():
    listas_dicts = []
    urls = get_urls()
    try:
        for url in urls:

            for item in url:

                print(item)
                driver.get(url)

                driver.implicitly_wait(7)
                dict_item = {}

                dict_item['paginaproduto'] = url

                try:
                    nomeproduto = driver.find_elements(By.XPATH,'//*[@id="prod-name"]')[0].text
                    dict_item['NomeProduto'] = nomeproduto
                except:
                    pass
                    
                try:
                    codigo  = driver.find_elements(By.XPATH,'//*[@id="prod-ref"]')[0].text
                    dict_item['CodigoProduto'] = codigo
                except:
                    pass
                        
                try:
                    dim_val1 = driver.find_elements(By.XPATH,'//*[@id="anclaProductDetail"]/div[2]/div/div[2]/div/div/div/form/div[1]/div[1]/div')
                    cont = 0
                    for x in dim_val1:
                        attr = x.text.split("\n")
                        for att in attr:
                            dict_item['Atributo'+str(cont)] = att
                            cont +=1
                except:
                    pass
                lista_imagens = []
                imagens = driver.find_elements(By.XPATH,'/html/body/div[1]/section/div[1]/div/div/div/div[3]/section/div/div[2]/div/section/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div/div/img')
                cont = 0
                for imagem in imagens:
                    dict_img = {}
                    dict_img['imagem'+str(cont)] = imagem.get_attribute('src')
                    lista_imagens.append(dict_img)
                    cont+=1

                atributo_k = driver.find_elements(By.XPATH,'//*[@id="first-container"]/div[3]/div/div/div[1]/p')
                atributo_v = driver.find_elements(By.XPATH,'//*[@id="first-container"]/div[3]/div/div/div[2]/p')
                cont = 0
                for keys in atributo_k:
                    dict_item[keys.text] = atributo_v[cont].text
                    cont+=1

                print(dict_item)
                dict_item['imagens'] = listas_dicts
                listas_dicts.append(dict_item)

               
                insert_produtos(nomeproduto = dict_item.get('NomeProduto'),
                 SKU=dict_item.get('CodigoProduto'), imagem=dict_item.get('imagens'), urlcoleta=dict_item.get('paginaproduto')
                 ,marca='Celite')
    except:
        pass
    data = pd.DataFrame(listas_dicts)
    data.to_excel(r'D:\produtoshausz\celite\pisoscelite.xlsx')
get_produtos()

