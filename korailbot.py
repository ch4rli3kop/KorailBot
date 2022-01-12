from re import L
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
from bot_token import Token

bot=commands.Bot(command_prefix='!')

work_list = {}

class Korail:
    def __init__(self):
        self.MEMID = ''
        self.PW = ''
        self.START = ''
        self.DEST = ''
        self.MONTH = ''
        self.DAY = ''
        self.TIME = ''
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')

    def _close_popup(self):
        windows = self.driver.window_handles
        if len(windows) > 1:
            for i in range(1, len(windows)):
                self.driver.switch_to.window(self.driver.window_handles[i])
                self.driver.close()
            self.driver.switch_to.window(windows[0])
        
    def _close_alert(self):
        # alert 창 제거
        try:
            while True:
                #WebDriverWait(self.driver, 3).until(EC.alert_is_present()) # 없어도 잘 됨
                alert_obj = self.driver.switch_to.alert
                #print(alert_obj.text)
                alert_obj.accept()
        except:
            print('alert 종료')
        finally:
            self.driver.switch_to.window(self.driver.window_handles[0])

    def korail_login(self, id, pw):
        self.MEMID = id
        self.PW = pw

        self.driver.get('https://www.letskorail.com/korail/com/login.do')
        self._close_popup()
        
        self.driver.find_element_by_id('txtMember').send_keys(self.MEMID)
        self.driver.find_element_by_id('txtPwd').send_keys(self.PW)
        self.driver.find_element_by_class_name('btn_login').click()
        time.sleep(0.2)
        login_success = self.driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[1]/div/ul/li[2]')
        print(login_success)
        if len(login_success) > 0:
            self._close_popup()
            return True
        self.korail_login(id, pw)

    def _parse_table(self, page_code):
        soup = BeautifulSoup(page_code, 'lxml')
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

    def korail_search(self, start, dest, month, day, hour):
        self.START = start
        self.DEST = dest
        self.MONTH = month
        self.DAY = day
        self.TIME = hour

        self.driver.get('https://www.letskorail.com/ebizprd/EbizPrdTicketpr21100W_pr21110.do')
        
        self._close_alert()
        self._close_popup()

        self.driver.find_element_by_id('start').clear()
        self.driver.find_element_by_id('start').send_keys(self.START)
        self.driver.find_element_by_id('get').clear()
        self.driver.find_element_by_id('get').send_keys(self.DEST)
        selecter = Select(self.driver.find_element_by_id('s_month'))
        selecter.select_by_value(self.MONTH)
        selecter = Select(self.driver.find_element_by_id('s_day'))
        selecter.select_by_value(self.DAY)
        selecter = Select(self.driver.find_element_by_id('s_hour'))
        selecter.select_by_value(self.TIME)
        self.driver.find_element_by_class_name('btn_inq').click()

        self._close_alert()
        self._close_popup()
        time.sleep(0.2)

        pages = self.driver.page_source
        result_table = self._parse_table(pages)
        return result_table
        

    def korail_reserve(self, num, royal = None):
    
        button_name = 'btnRsv1_' + num  
        if royal == '우등':
            button_name = 'btnRsv2_' + num

        # loop until find canceled ticket
        # 예약하기 버튼 검색
        button = self.driver.find_elements_by_name(button_name)
        while len(button) == 0:
            # 조회하기 버튼 클릭
            try:
                self.driver.find_element_by_class_name('btn_inq').click()
                time.sleep(0.1)
                self._close_alert()
                self._close_popup()
                button = self.driver.find_elements_by_name(button_name)
            except:
                # 캡차 검사 창이 뜰 경우 재접속하여 진행
                self.korail_quit()
                self.__init__()
                self.korail_login(self.MEMID, self.PW)
                self.korail_search(self.START, self.DEST, self.MONTH, self.DAY, self.TIME)

        # 예약하기 버튼 클릭
        self.driver.find_element_by_name(button_name).click()
        
        # alert 창 제거
        self._close_alert()
        self._close_popup()

        # 경유일 경우 확인 창 넘겨줘야 함
        iframe = self.driver.find_elements_by_id('embeded-modal-traininfo')
        if len(iframe) > 0:
            self.driver.switch_to.frame(iframe[0])
            btn = self.driver.find_elements_by_class_name('btn_blue_ang')
            print(btn)
            if len(btn) > 0:
                btn[0].click()
            self.driver.switch_to.default_content()

        self.driver.find_element_by_id('btn_next').click()
        
        self._close_alert()
        self._close_popup()

        self.driver.find_elements_by_class_name('btn_blue_ang')[3].click()
        return True

    def korail_quit(self):
        self.driver.quit()

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
    work_list['charlie'] = Korail()
    await ctx.send('다음의 명령어를 차례대로 입력해주세요.\n!login MEMBERSHIP_ID PW\n!search START DEST MONTH DAY TIME(시)\n!select NUM')

@bot.command()
async def login(ctx, *, text = None):
    if text != None:
        args = text.split(' ')
        if len(args) != 2:
            await ctx.send('인자를 확인해주세요.\nex) !login 171231231 찬희123')
            return
        login_ID = args[0]
        login_PW = args[1]
        try:
            login_success = work_list['charlie'].korail_login(login_ID, login_PW)
            if login_success:
                await ctx.send('로그인이 완료되었습니다.')
        except:
            ctx.send('로그인 오류!\n인자를 확인해주세요.\nex) !login 171231231 찬희123')
    else:
        await ctx.send('인자를 확인해주세요.\nex) !login 171231231 찬희123')

@bot.command()
async def search(ctx, *, text = None):
    if text != None:
        args = text.split(' ')
        start = args[0]
        dest = args[1]
        month = args[2]
        day = args[3]
        time = args[4]
        if len(args) != 5:
            await ctx.send('인자를 확인해주세요.\nex) !search 영등포 조치원 1 24 4')
            return

        if len(month) < 2:
            month = '0' + month
        if len(day) < 2:
            day = '0' + day
        if len(time) < 2:
            time = '0' + time

        try:
            result = work_list['charlie'].korail_search(start, dest, month, day, time)
        except:
            await ctx.send('실행오류.')
            return
        await ctx.send(result)
        await ctx.send('20분 이내 열차는 예약할 수 없습니다.')

@bot.command()
async def select(ctx, *, text = None):
    if text != None:
        select = text.split(' ')[0]
        try:
            result = work_list['charlie'].korail_reserve(select)
            if result:
                work_list['charlie'].korail_quit()
                del work_list['charlie']
        except RuntimeError as e:
            print(e)
            await ctx.send('인자를 확인해주세요.\nex)!select 3')
            return
        await ctx.send('장바구니에 담았습니다.')
        await ctx.send('봇을 종료합니다.')
    else:
        await ctx.send('인자를 확인해주세요.')

bot.run(Token)
