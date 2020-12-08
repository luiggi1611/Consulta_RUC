# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 13:28:52 2020

@author: serv_prog021
"""

from bs4 import BeautifulSoup
import requests
import urllib.request
from pytesseract import image_to_string
from PIL import Image ##pillow
import pytesseract
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os 
import pandas as pd
import re
os.chdir(r"C:\Users\luigg\OneDrive\Escritorio\Proyecto_Corrupcion")

rucs= pd.read_csv("provedores_consolidados.csv")
# VENCER EL CODIGO CAPTCHA !!!!!!!!
def get_captcha_text(location, size):
    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'
    im = Image.open('screenshot.png')  # uses PIL library to open image in memory
    left = location['x']-270
    top = location['y']+5
    right = location['x'] + size['width'] -230
    bottom = location['y'] + size['height']+1
    im = im.crop((left, top, right, bottom))  # defines crop points
    im.save('screenshot.png')
    captcha_text = image_to_string(Image.open('screenshot.png'))
    return captcha_text


rucs=rucs['RUCPROVEEDOR'].unique()
url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/frameCriterioBusqueda.jsp'
driver = webdriver.Chrome(executable_path="Drivers/chromedriver.exe")
Base_rucs_empresa=pd.DataFrame()
Base_rucs_persona=pd.DataFrame()
def normalize(s):
    replacements = (
        ("Á", "A"),
        ("É", "E"),
        ("Í", "I"),
        ("Ó", "O"),
        ("Ú", "U"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s
corrida=0
interval=0
while interval<len(rucs):
    if corrida==5:
        interval+=1
        corrida=0
    try:
        driver.get(url)
        driver.set_window_size(1200, 550)
        element = driver.find_element_by_xpath('/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[1]/td[7]')  # find part of the page you want image of
        location = element.location
        size = element.size
        driver.save_screenshot('screenshot.png')
        user_id = driver.find_element_by_xpath('/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[1]/td[3]/div/input')
        user_id.send_keys(rucs[interval].astype(str))
        captcha = driver.find_element_by_xpath('/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[1]/td[6]/input')
        captcha.clear()
        captcha_text = get_captcha_text(location, size)
        captcha_text=normalize(captcha_text)
        captcha_text =re.sub(r'[^\w]', '', captcha_text )
        captcha_text=captcha_text.replace('_','O')
        captcha_text=captcha_text.replace('1','I')
        captcha_text=captcha_text.replace('0','O')
        if any(map(str.isdigit, captcha_text)):
            captcha_text='HOLA'
        if len(captcha_text)==4:
            print('ok')
        else:
            captcha_text='HOLA'
        captcha.send_keys(captcha_text)
        driver.find_element_by_xpath('/html/body/form/table/tbody/tr/td/table[2]/tbody/tr[1]/td[7]/input').click()
        driver.switch_to_window(driver.window_handles[1])
        if rucs[interval].astype(str)[0]=='2':
            conteo = [2,2,2,4,2,2,2,4,2,2,2,2,2,2,2,2]
            data = list([])
            driver.find_element_by_xpath("//table[1]/tbody/tr["+str(9+1)+"]/td["+str(1+1)+"]").text
            for i in range(0,16):
                for j in range(0,conteo[i]):
                    data.append(driver.find_element_by_xpath("//table[1]/tbody/tr["+str(i+1)+"]/td["+str(j+1)+"]").text)
            import pandas as pd
            pares = list([])
            impares = list([])
            for i in range(0,36,2):
                pares.append(data[i])
                
            for j in range(1,36,2):
                impares.append(data[j])
            tmp=pd.DataFrame([impares],columns=pares)
            tmp['Actividad(es) Económica(s):']=" ".join(tmp['Actividad(es) Económica(s):'].str.strip()).replace("\n", " ")
            Base_rucs_empresa=Base_rucs_empresa.append(tmp)
            interval+=1
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
            corrida=0
        elif rucs[interval].astype(str)[0]!='1':
            interval+=1
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
            corrida=0
        else:
            conteo = [2,2,2,2,4,2,2,2,4,2,2,2,2,2,2,2,2]

            data = list([])
            for i in range(0,17):
                for j in range(0,conteo[i]):
                    data.append(driver.find_element_by_xpath("//table/tbody/tr["+str(i+1)+"]/td["+str(j+1)+"]").text)
            pares = list([])
            impares = list([])
            for i in range(0,36,2):
                pares.append(data[i])
                
            for j in range(1,36,2):
                impares.append(data[j])
            tmp=pd.DataFrame([impares],columns=pares)
            Base_rucs_persona=Base_rucs_persona.append(tmp)
            interval+=1
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
            corrida=0
    except:
        corrida+=1
        driver.close()
        driver.switch_to_window(driver.window_handles[0])
    



