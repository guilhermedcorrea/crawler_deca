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
import re
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
                  {"nomeproduto":kwargs.get("nomeproduto"),"SKU":kwargs.get("SKU"),
                  "urlcoleta":kwargs.get("paginaproduto")
                  ,"ean":kwargs.get("ean"),"imagem":kwargs.get("imagem"),"marca":"Roca Metais"
                  }
                ]
            )




urls=["https://www.br.roca.com/produtos/chuveiros",
"https://www.br.roca.com/produtos/smart-toilets","https://www.br.roca.com/produtos/bacias-sanitarias?page=3"
,"https://www.br.roca.com/produtos/pias-cubas-cozinha?page=3","https://www.br.roca.com/produtos/assentos-tampas-sanitarias?page=1"
,"https://www.br.roca.com/produtos/espelhos","https://www.br.roca.com/produtos/banheiras","https://www.br.roca.com/produtos/bides"]



def scroll() -> None:
    driver.implicitly_wait(7)
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True

def get_url_produtos():
    scroll()
    try:
        produtos = driver.find_elements(
            By.XPATH,'/html/body/div[3]/section/div/div/div/div/div[5]/section/div/div[2]/div/section[3]/div[1]/div[3]/div/div/div/div/div[1]/div[1]/div/a')
        for produto in produtos:
          yield produto.get_attribute('href')

    except Exception as e:
        print("Erro", e)


def pagination():
    lista_urls = []
    for url in urls:
        try:
            if re.search('[?page=]\d+',url):
                url = url.split("?page=")
                value = url[0] + '?page='
                for i in range(int(url[-1])):
                    url_produto = value+f"{i}"
                    driver.get(url_produto)
                    produtos_url = get_url_produtos()
                    for produto in produtos_url:
                        lista_urls.append(produto)
        except Exception as e:
            print("error")
                  
        else:
            produtos_url = get_url_produtos()
            for produto in produtos_url:
                lista_urls.append(produto)
            
    return   lista_urls    

def extract_item():
    litas_dicts = []
    driver.implicitly_wait(7)
    urls_produtos = pagination()
    for produtos in urls_produtos:
        driver.get(produtos)
        dict_item = {}
        time.sleep(1)
        dict_item['paginaproduto'] = produtos
        try:
            sku = driver.find_elements(By.XPATH,'//*[@id="prod-ref"]')[0].text
            dict_item['SKU'] = sku
        except Exception as e:
            sku = driver.find_elements(By.ID,'prod-ref')[0].text
        except:
            Error='notfound'
           

        try:
            nomeproduto = driver.find_elements(By.XPATH,'//*[@id="prod-name"]')[0].text
            dict_item['NomeDoProduto'] = nomeproduto
        except Exception as e:
            print("error",e)

        try:
            attr1 = driver.find_elements(By.XPATH,'//*[@id="anclaProductDetail"]/div[2]/div/div[2]/div/div/div/form/div[1]/div[1]/div')
            for att in attr1:
                dict_item['dimensoes'] = att.text
        except Exception as e:
            print("error", e)
        try:
            pdf_atributo = driver.find_elements(By.XPATH,'//*[@id="productPDFLink"]')[0].get_attribute('href')
            dict_item['informacoestecnicas'] = pdf_atributo
        except Exception as e:
            print("error",e)

        try:
            medidas = driver.find_elements(By.XPATH,'//*[@id="anclaProductDetail"]/div[2]/div/div[2]/div/div/div/form/div[1]/div[2]/div/a[2]/span/img')[0].get_attribute("src")
            dict_item['Medidas'] = medidas
        except Exception as e:
            print("error",e)
        
        try:
            lista_imagens = []
            imagens = driver.find_elements(By.XPATH,'//*[@id="anclaProductDetail"]/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div/div/a/img')
            cont = 0
            for imagem in imagens:
                dict_img = {}
                dict_img[f'{sku}_'+str(cont)] = imagem.get_attribute('src')
                lista_imagens.append(dict_img)
                cont +=1
                
        except Exception as e:
            dict_img['imagem'] = 'notfound'
            print("error", e)
        

        
    
        dict_item['imagens'] = lista_imagens
        insert_produtos(nomeproduto=str(dict_item.get('NomeDoProduto')), SKU=str(dict_item.get('SKU')),imagem=str(dict_item.get('imagens'))
        , paginaproduto=str(dict_item.get('paginaproduto')))
        #scroll()

        
        '''
        try:
            video = driver.find_elements(By.XPATH,'//*[@id="portlet_VideoBanner_INSTANCE_DoEeK5nnKKh8"]/div/div[2]/div/link')[0].get_attribute("href")
            dict_item['video'] = video
        except Exception as e:
            print("error",e)
        try:
            atributosk = driver.find_elements(By.XPATH,'//*[@id="first-container"]')
            for attri in atributosk:
                caracteristicas = attri.text.split("\n")
                for caracteristica in caracteristicas:
                    caract = caracteristica.split(":")
                    if len(caract) >=  2:
                        dict_item[caract[0]] = caract[1:][0]
                    else:
                        cont = 0
                        for atributo in caract:
                            dict_item['Atributo'+str(cont)] = atributo
                            cont+=1

        except Exception as e:
            print(e)

        '''
      
     
        #print(dict_item)
        litas_dicts.append(dict_item)
        
       

       
       
    #data = pd.DataFrame(litas_dicts)
    #data.to_excel(r"D:\produtoshausz\gruporoca\rocametas04111.xlsx")


extract_item()
