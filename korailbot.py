from re import L
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from bot_token import Token

bot=commands.Bot(command_prefix='!')

MEMID = ''
PW = ''
START = ''
DEST = ''
MONTH = ''
DAY = ''
TIME = ''
driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')


def korail_login(id, pw):
    #korail_init()
    global MEMID, PW, driver
    MEMID = id
    PW = pw

    driver.get('https://www.letskorail.com/korail/com/login.do')
    windows = driver.window_handles
    if len(windows) > 1:
        for i in range(1, len(windows)):
            driver.switch_to.window(driver.window_handles[i])
            driver.close()
    driver.switch_to.window(windows[0])
    time.sleep(0.2)

    driver.find_element_by_id('txtMember').send_keys(MEMID)
    driver.find_element_by_id('txtPwd').send_keys(PW)
    driver.find_element_by_class_name('btn_login').click()
    time.sleep(0.2)
    windows = driver.window_handles
    if len(windows) > 1:
        for i in range(1, len(windows)):
            driver.switch_to.window(driver.window_handles[i])
            driver.close()
    driver.switch_to.window(windows[0])

def korail_search(start, dest, month, day, hour):
    global START, DEST, MONTH, DAY, TIME, driver
    START = start
    DEST = dest
    MONTH = month
    DAY = day
    TIME = hour

    driver.get('https://www.letskorail.com/ebizprd/EbizPrdTicketpr21100W_pr21110.do')
    driver.find_element_by_id('start').clear()
    driver.find_element_by_id('start').send_keys(START)
    driver.find_element_by_id('get').clear()
    driver.find_element_by_id('get').send_keys(DEST)
    selecter = Select(driver.find_element_by_id('s_month'))
    selecter.select_by_value(MONTH)
    selecter = Select(driver.find_element_by_id('s_day'))
    selecter.select_by_value(DAY)
    selecter = Select(driver.find_element_by_id('s_hour'))
    selecter.select_by_value(TIME)
    driver.find_element_by_class_name('btn_inq').click()
    time.sleep(0.9)

    pages = driver.page_source
    soup = BeautifulSoup(pages, 'lxml')
    table = soup.find('table', id='tableResult')
    res = []
    row = []
    for tr in table.find_all('tr'):
        for td in tr.find_all('td'):
            text = td.text.strip()
            text = text.replace('\r', '')
            text = text.replace('\t', '')
            text = text.replace('\n', '')
            row.append(text)
        if row != []:
            res.append(row)
        row = []
    table_df = pd.DataFrame(res)
    columns = []
    for th in table.find_all('th'):
        columns.append(th.text.strip())
    table_df.columns = columns
    table_df2 = table_df.drop(['특실/우등실', '유아', '자유석', '예약대기', '정차역(경유)', '차량유형/편성정보', '운임요금', '일반실'], axis=1)
    return table_df2

def korail_reserve(num):
    global driver
    button_name = 'btnRsv1_' + num  
    button = driver.find_elements_by_name(button_name)
    while len(button) == 0:
        driver.find_element_by_class_name('btn_inq').click()
        time.sleep(0.2)
        button = driver.find_elements_by_name(button_name)

    driver.find_element_by_name(button_name).click()
    alert_obj = driver.switch_to.alert
    alert_obj
    alert_obj.accept()
    alert_obj = driver.switch_to.alert
    alert_obj.accept()
    driver.find_element_by_id('btn_next').click()
    driver.find_elements_by_class_name('btn_blue_ang')[3].click()
    driver.quit()
    #TODO: while until reserving successfully

@bot.event
async def on_ready():
    print(f"봇={bot.user.name}로 연결중")
    print('연결이 완료되었습니다.')
    await bot.change_presence(status=discord.Status.online, activity=None)

@bot.command()
async def hi(ctx):
    '''
    인사하기
    '''
    await ctx.send('안녕하세요 봇이 정상적으로 작동중입니다.')

@bot.command()
async def hihi(ctx, *, text = None):
    print(text)
    if text != None:
        await ctx.send(text)
    else:
        await ctx.send('인자를 확인해주세요')

@bot.command()
async def reserve(ctx):
    print('Reserving 동작 중')
    await ctx.send('다음의 명령어를 차례대로 입력해주세요.\n!login MEMBERSHIP_ID PW\n!search START DEST MONTH DAY TIME\n!select NUM')

@bot.command()
async def login(ctx, *, text = None):
    if text != None:
        args = text.split(' ')
        if len(args) != 2:
            await ctx.send('인자를 확인해주세요.')
            return
        login_ID = args[0]
        login_PW = args[1]
        try:
            korail_login(login_ID, login_PW)
        except:
            ctx.send('인자를 확인해주세요.\nex) !login 17123123 chanchanpw')
        await ctx.send('로그인이 완료되었습니다.')
    else:
        await ctx.send('인자를 확인해주세요.')

@bot.command()
async def search(ctx, *, text = None):
    if text != None:
        args = text.split(' ')
        start = args[0]
        dest = args[1]
        month = args[2]
        day = args[3]
        time = args[4]
        if len(month) < 2:
            month = '0' + month
        if len(day) < 2:
            day = '0' + day
        if len(time) < 2:
            time = '0' + time
        try:
            result = korail_search(start, dest, month, day, time)
        except:
            ctx.send('인자를 확인해주세요.\nex) !search 영등포 조치원 1 24 4')
            return
        await ctx.send(result)
    else:
        await ctx.send('인자를 확인해주세요.')

@bot.command()
async def select(ctx, *, text = None):
    if text != None:
        select = text.split(' ')[0]
        try:
            korail_reserve(select)
        except:
            await ctx.send('인자를 확인해주세요.\nex)!select 3')
            return
        await ctx.send('장바구니에 담았습니다.')
    else:
        await ctx.send('인자를 확인해주세요.')

bot.run(Token)
