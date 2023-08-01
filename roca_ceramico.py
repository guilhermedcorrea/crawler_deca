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
from typing import Literal, List, Any
from itertools import chain
from config import get_engine
from tabela import ImagensColetadas
from sqlalchemy import insert

options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")
options.add_argument('--disable-infobars')
driver = webdriver.Chrome(options=options, executable_path=r"D:\produtoshausz\chromedriver\chromedriver.exe")



def insert_produtos(*args, **kwargs):
    engine = get_engine()
    with engine.connect() as conn:

        result = conn.execute(
                insert(ImagensColetadas),
                [
                  {"nomeproduto":kwargs.get("nomeproduto"),"SKU":kwargs.get("SKU")
                  ,"ean":kwargs.get("ean"),"imagem":kwargs.get("imagem"),"urlcoleta":kwargs.get("urlcoleta")
                  }
                ]
            )


def scroll() -> None:
    driver.implicitly_wait(7)
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True


def get_categorias() -> list:
    lista_urls: list = []
    driver.implicitly_wait(7)
    driver.get('https://www.rocaceramica.com.br/produtos/')
    scroll()
    urlscategoria = driver.find_elements(By.XPATH,'/html/body/section[2]/div/div/div/div[1]/a')
    for urls in urlscategoria:
        lista_urls.append(urls.get_attribute('href'))
        print(urls.get_attribute('href'))
    
    return lista_urls


def get_urls() -> list:
    driver.implicitly_wait(7)
    lista_urls: list = []

    categorias = get_categorias()
    for categoria in categorias:
        driver.get(categoria)

        time.sleep(1)
        dict_item = {}
        linha = driver.find_elements(By.CSS_SELECTOR,'body > section.box-header.container-fluid > div > h1')[0].text
        dict_item['Linha'] = linha

        descricao = driver.find_elements(By.XPATH,'/html/body/section[2]/div/div/div/p')[0].text
        dict_item['descricao'] = descricao


        urls = driver.find_elements(By.XPATH,'/html/body/section[3]/div/div/a')
        for url in urls:
            dict_item['urlcategoria'] = categoria
            dict_item['urlproduto'] = url.get_attribute('href')         
            lista_urls.append(dict_item)

    return lista_urls


def get_produtos() -> None:
    lista_dicts = []
    driver.implicitly_wait(7)
    urls = get_urls()
    for url in urls:
        if isinstance(url.get('urlproduto'), str):
            dict_produtos = {}
            driver.get(url.get('urlproduto'))

            dict_produtos['urlproduto'] = url.get('urlproduto')
            dict_produtos['urlcategoria'] = url.get('urlcategoria')
            dict_produtos['descricao'] = url.get('descricao')
            dict_produtos['Linha'] = url.get('Linha')

            lista_imagens = []
            imagens = driver.find_elements(By.XPATH,'/html/body/section[2]/div/div[1]/div/div[2]/div[1]/div/img')
            cont = 0
            for imagem in imagens:
                dict_img = {}
                dict_img['imagem'+str(cont)] = imagem.get_attribute('src')
                lista_imagens.append(dict_img)
                cont +=1
            
            try:
                nome = driver.find_elements(By.XPATH,'/html/body/section[2]/div/div[2]/div[1]/div/h2')[0].text
                dict_produtos['NomeProduto'] = nome
            except IndexError as e:
                error='NotFound'
            
            try:
                codigo = driver.find_elements(By.XPATH,'/html/body/section[2]/div/div[2]/div[1]/div/div[1]/div[2]')[0].text
                dict_produtos['SKU'] = codigo
            except IndexError as e:
                Error='NotFound'

            try:
                tipo = driver.find_elements(By.XPATH,'/html/body/section[2]/div/div[2]/div[1]/div/div[1]/div[1]')[0].text
                dict_produtos['Tipo'] = tipo
            except IndexError as e:
                Error='NotFound'

            atributos_k = driver.find_elements(By.CLASS_NAME,'produto-label')
            atributos_v = driver.find_elements(By.CLASS_NAME,'produto-info')
            cont = 0
            for atributok in atributos_k:
                dict_produtos[atributok.text] = atributos_v[cont].text
                cont +=1
          
            table_label = driver.find_elements(By.XPATH,'/html/body/section[3]/div[2]/div[1]/table/tbody/tr/td[1]')
            table_labelv = driver.find_elements(By.XPATH,'/html/body/section[3]/div[2]/div[1]/table/tbody/tr/td[2]')
            cont = 0
            for tale in table_label:
                dict_produtos[tale.text] = table_labelv[cont].text
                cont +=1
            
            table_label2 = driver.find_elements(By.XPATH,'/html/body/section[3]/div[4]/div[1]/table/tbody/tr/td[1]')
            table_labelvalue2 = driver.find_elements(By.XPATH,'/html/body/section[3]/div[4]/div[1]/table/tbody/tr/td[2]')
            cont = 0
            for table in table_label2:
                dict_produtos[table.text] = table_labelvalue2[cont].text
                cont +=1

            table_label3 = driver.find_elements(By.XPATH,'/html/body/section[3]/div[2]/div[2]/table/tbody/tr/td[1]')
            table_label3v = driver.find_elements(By.XPATH,'/html/body/section[3]/div[2]/div[2]/table/tbody/tr/td[2]')
            cont = 0
            for table in table_label3:
                dict_produtos[table.text] = table_label3v[cont].text
                cont+=1

            table_label4 = driver.find_elements(By.XPATH,'/html/body/section[3]/div[4]/div[2]/table/tbody/tr/td[1]')
            table_label4v = driver.find_elements(By.XPATH,'/html/body/section[3]/div[4]/div[2]/table/tbody/tr/td[1]')
            cont = 0
            for table in table_label4:
                dict_produtos[table.text] = table_label4v[cont].text
                cont+=1
            dict_produtos['imagens'] = lista_imagens
            print(dict_produtos)
            insert_produtos(nomeproduto = str(dict_produtos.get('NomeProduto'))
            , SKU = str(dict_produtos.get('SKU')), , urlcoleta=str(dict_produtos.get('urlproduto')))

     
            lista_dicts.append(dict_produtos)
    
    data = pd.DataFrame(lista_dicts)
    data.to_excel("rocapisos.xlsx")
 

get_produtos()