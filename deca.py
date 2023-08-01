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
from config import get_engine
from sqlalchemy import insert
from config import get_engine
from tabela import cadastroprodutos


def insert_produtos(*args, **kwargs):
    engine = get_engine()
    with engine.connect() as conn:
        try:
            result = conn.execute(
                insert(cadastroprodutos),
                [
                  {"sku":kwargs.get("sku"),"marca":kwargs.get("marca"),"nomeproduto":kwargs.get("nomeproduto")
                    ,"atributos":kwargs.get("atributos"),
                  "urlproduto":kwargs.get("urlproduto"),"origem":kwargs.get("origem"),"imagens":kwargs.get("imagem")
                  }
                ]
            )
        except Exception as e:
            print("error", e)

options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")
options.add_argument('--disable-infobars')
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options, executable_path=r"D:\produtoshausz\chromedriver\chromedriver.exe")


def criar_template(keys):
    produtos = {}
    lista1 = []
    lista2 = []
    for dic in keys:
        if dic !='dicbasico':
            th = f'<th scope="col">{dic}</th>'
            tr = f'<td>{keys[dic]}</td>'
            lista1.append(th)
            lista2.append(tr)

    template = """
            <table class="table">
            <thead>
            <tr>
                {}
            </tr>
            </thead>
            <tbody>
            <tr>
                {}
            </tr>
            </tbody>
            </table>""".format([x.split("\n") for x in lista1], [x.split("\n") for x in lista2])

    body = template.replace("[","").replace("]","").replace("'","").replace(",","\n").strip()
    produtos['atributos'] = body
    return produtos

urls = pd.read_excel(r'D:\produtoshausz\deca\banheiro-e-lavabo.xlsx')
lista_urls = urls['urls'].to_list()
           
def get_produtos():
    for listas in lista_urls:
        driver.get(listas)
        dict_produtos = {}
        dic_basico = {}
    
        
        try:
            nome = driver.find_elements(By.XPATH,'//*[@id="produto"]/div/div/div[3]/div[3]/h1')[0].text
            dict_produtos['NomeProduto'] = nome
            dic_basico['NomeProduto'] = nome
            dic_basico['urlproduto'] = listas
        except:
            pass
        
        try:
            sku = driver.find_elements(By.XPATH,'//*[@id="produto"]/div/div/div[3]/div[1]/div[2]')[0].text.split()[-1]
            dict_produtos['CodigoProduto'] = sku.strip()
            dic_basico['CodigoProduto']= sku.strip()
        except:
            pass
        lista_img = []
        imagens = driver.find_elements(By.XPATH,'//*[@id="produto"]/div/div/div[2]/div/img')
        cont = 0
        for imagem in imagens:
           
            dic_basico['imagem'+str(cont)] = imagem.get_attribute('src')
            cont +=1
           
        try:
            json_produtos = driver.find_elements(By.CSS_SELECTOR,'#__NEXT_DATA__')
            for jsons in json_produtos:
                produto = json.loads(jsons.get_attribute('textContent'))
                atributos = produto['props']['pageProps']['product']['attributes']
                item = {}
                item['ProductDescription'] = atributos['ProductDescription']
                item['NameInvoice'] = atributos['NameInvoice']
                item['EAN'] = atributos['EAN']
                item['ReferenceCode'] = atributos['ReferenceCode']
                item['MaterialCode'] = atributos['MaterialCode']
                item['Height'] = atributos['Height']
                item['Width'] = atributos['Width']
                item['Length'] = atributos['Length']
                item['Weight'] = atributos['Weight']
                item['Keyword'] = atributos['Keyword']
                item['NCM'] = atributos['NCM']
                item['TechnicalDrawing'] = atributos['TechnicalDrawing']
                item['BasicComposition'] = atributos['BasicComposition']
                item['Ambience'] = atributos['Ambience']
                dict_produtos.update(item)
        except:
            print("error")
        dict_produtos['imagens'] = lista_img
        dict_produtos['dicbasico'] = dic_basico
        
        time.sleep(1)
        cores_k = driver.find_elements(By.XPATH,'//*[@id="produto"]/div/div/div[3]/div[5]/a')
        urls_cores = driver.find_elements(By.XPATH,'//*[@id="produto"]/div/div/div[3]/div[5]/a')
        cont = 0
        for keys in cores_k:
            dict_produtos[keys.text] = urls_cores[cont].get_attribute('href')
            cont+=1
        
        categorias = driver.find_elements(By.XPATH,'//*[@id="produto"]/div/div/div[3]/div[1]/div[1]/a')
        for categoria in categorias:
            dict_produtos[categoria.text] = categoria.get_attribute('href')
        print(dic_basico)
        yield dict_produtos
    df = pd.DataFrame(dic_basico)
    df.to_excel("deca001.xlsx")
dicts = get_produtos()
for dic in dicts:
    produtos = {}
    item = criar_template(dic)

    
 
    produtos.update(item)
    #produtos['TEMPLATE'] = item
    try:
        produtos['SKU'] = dic.get('dicbasico')['CodigoProduto']
    except:
        pass
    try:
        produtos['NomeProduto'] = dic.get('dicbasico')['NomeProduto']
    except:
        pass
    try:
        produtos['imagens'] = dic.get('dicbasico')['imagem0']
    except:
        pass
  
    try:
        produtos['Marca'] = 'Deca'
    except:
        pass
    try:
        produtos['urlproduto'] = dic.get('urlproduto')
    except:
        pass
    try:
        produtos['origem'] = 'www.deca.com.br'
    except:
        pass

    try:
    
        insert_produtos( marca = produtos['Marca'],
        nomeproduto = produtos['NomeProduto'],sku=produtos['SKU'], urlproduto = produtos['urlproduto']
        , origem=produtos['origem'],atributos = produtos['atributos'], imagem = produtos['imagens'])
    except:
        pass

  

  

    
