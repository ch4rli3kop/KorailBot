#!/usr/bin/python3
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import pandas as pd

MEMBERSHIP_ID = 'MEMBERSHIP_ID'
PASSWD = 'PASSWD'
START = '서울'
DEST = '조치원'
MONTH = '01'
DAY = '14'

driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
# driver.get('https://www.letskorail.com/ebizprd/prdMain.do')
driver.get('https://www.letskorail.com/korail/com/login.do')
windows = driver.window_handles
if len(windows) > 1:
    for i in range(1, len(windows)):
        driver.switch_to.window(driver.window_handles[i])
        driver.close()
driver.switch_to.window(windows[0])
time.sleep(0.2)

driver.find_element_by_id('txtMember').send_keys(MEMBERSHIP_ID)
driver.find_element_by_id('txtPwd').send_keys(PASSWD)
driver.find_element_by_class_name('btn_login').click()
time.sleep(0.2)

windows = driver.window_handles
if len(windows) > 1:
    for i in range(1, len(windows)):
        driver.switch_to.window(driver.window_handles[i])
        driver.close()
driver.switch_to.window(windows[0])

# 일반승차권 조회
driver.get('https://www.letskorail.com/ebizprd/EbizPrdTicketpr21100W_pr21110.do')
driver.find_element_by_id('start').clear()
driver.find_element_by_id('start').send_keys(START)
driver.find_element_by_id('get').clear()
driver.find_element_by_id('get').send_keys(DEST)
selecter = Select(driver.find_element_by_id('s_month'))
selecter.select_by_value(MONTH)
selecter = Select(driver.find_element_by_id('s_day'))
selecter.select_by_value(DAY)

## 조회하기
time.sleep(2)

driver.find_element_by_class_name('btn_inq').click()
time.sleep(0.2)

pages = driver.page_source
soup = BeautifulSoup(pages, 'html.parser')
table = soup.select_one('table')
print(table)
tableFrame = pd.DataFrame(table)
print(tableFrame)
# for info in table.select('td'):
#     a = info.text
#     print(a.split(''))
