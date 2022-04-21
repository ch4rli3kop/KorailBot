from re import L
import discord
import asyncio
from asyncio import Queue
import time
from discord.ext import commands
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
from bot_token import Token
import logging
#from pyvirtualdisplay import Display

logger = logging.getLogger('login_log')
logger.setLevel(level=logging.WARNING)

bot = commands.Bot(command_prefix='!', help_command=None)

work_list = {}
queue = asyncio.Queue
loop = asyncio.get_event_loop()

class Korail:
    def __init__(self):
        self.MEMID = ''
        self.PW = ''
        self.START = ''
        self.DEST = ''
        self.MONTH = ''
        self.DAY = ''
        self.TIME = ''
        self.init()

    def init(self):
        #self.virtual_display = Display(visible=0, size=(800, 600)).start()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36')
        chrome_options.add_argument('Accept=*/*')
        chrome_options.add_argument('Sec-Fetch-Site=same-origin')
        chrome_options.add_argument('Sec-Fetch-Mode=no-cors')
        chrome_options.add_argument('Sec-Fetch-Dest=script')
        chrome_options.add_argument("lang=ko_KR")
        chrome_options.add_argument('--user-data-dir=~/.config/google-chrome')
        #chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=chrome_options)
        #self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')

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
            pass
        finally:
            self.driver.switch_to.window(self.driver.window_handles[0])

    def korail_login(self, id, pw):
        self.MEMID = id
        self.PW = pw

        self.driver.get('https://www.letskorail.com/korail/com/login.do')
        
        self._close_alert()
        self._close_popup()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "btn_login")))
        self._close_alert()
        self._close_popup()


        self.driver.find_element_by_id('txtMember').send_keys(self.MEMID)
        self.driver.find_element_by_id('txtPwd').send_keys(self.PW)
        self.driver.find_element_by_class_name('btn_login').click()
#        asyncio.sleep(1)
        self.driver.get('https://www.letskorail.com/ebizprd/prdMain.do')
        self._close_alert()
        self._close_popup()
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "log_nm")))
        self._close_alert()
        self._close_popup()
        #print(self.driver.page_source)
        # with open('./page_source.txt', 'w') as fp:
        #     fp.write(self.driver.page_source)
        login_success = self.driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[1]/div/ul/li[2]')
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
        
        #WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "ticket_box")))
        self._close_alert()
        self._close_popup()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "btn_inq")))
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
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "divResult")))

        pages = self.driver.page_source
        result_table = self._parse_table(pages)
        return result_table
        

    async def korail_reserve(self, num, royal = None):
    
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
                self._close_alert()
                self._close_popup()
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, "divResult")))
                button = self.driver.find_elements_by_name(button_name)
                # 비동기 작업 전환하려면 sleep 필수
                await asyncio.sleep(0)
            except:
                # 캡차 검사 창이 뜰 경우 재접속하여 진행
                self.korail_quit()
                self.init()
                self.korail_login(self.MEMID, self.PW)
                self.korail_search(self.START, self.DEST, self.MONTH, self.DAY, self.TIME)

        # 예약하기 버튼 클릭
        self.driver.find_element_by_name(button_name).click()
        
        # alert 창 제거
        self._close_alert()
        self._close_popup()

        # 20분 이내 예약일 시
        guidemsg = self.driver.find_elements_by_class_name('guide_msg')
        if len(guidemsg) > 0:
            if '20분 이내 열차는 예약하실 수 없습니다' in guidemsg[0].text:
                return False

        # 경유일 경우 확인 창 넘겨줘야 함
        iframe = self.driver.find_elements_by_id('embeded-modal-traininfo')
        if len(iframe) > 0:
            self.driver.switch_to.frame(iframe[0])
            btn = self.driver.find_elements_by_class_name('btn_blue_ang')
            #print(btn)
            if len(btn) > 0:
                btn[0].click()
            self.driver.switch_to.default_content()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "btn_next")))

        self.driver.find_element_by_id('btn_next').click()
        
        self._close_alert()
        self._close_popup()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn_blue_ang")))

        self.driver.find_elements_by_class_name('btn_blue_ang')[3].click()
        return True

    def korail_quit(self):
        self.driver.quit()
        #self.virtual_display.stop()

async def test_while(username):
    start = time.time()
    for i in range(0, 10000):
        await asyncio.sleep(0)
        print(username, i)
    print(time.time() - start)
    return 12

@bot.command()
async def hihi(ctx, *, text = None):
    print(text)
    if text != None:
        username = ctx.message.author.name
        await ctx.send(str(username) + '님이 테스트 중입니다.')
        print(username)
        task = asyncio.create_task(test_while(username))
        result = await task
        await ctx.send(str(result))
    else:
        await ctx.send('인자를 확인해주세요')

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="코레일봇 사용가이드", description="코레일예약봇에게 다음과 같이 **개인메시지**를 전송합니다. 메시지는 각각 응답을 받은 뒤 입력합니다.\n```!reserve\n!login {멤버십 아이디} {패스워드}\n!search {출발역} {도착역} {월} {일} {시}\n!select {선택번호}```", color=discord.Color.random())
    embed.set_author(name="ch4rli3kop", url="https://github.com/ch4rli3kop", icon_url="https://avatars.githubusercontent.com/u/35250476?s=400&u=b904844df4ef55a5dba52a232c70efc998372bf6&v=4")
    embed.add_field(name="!reserve", value="각 사용자에 대해 봇 사용을 준비합니다. 성공적으로 준비가 완료되면, 다음과 같은 메시지가 도착합니다. ```다음의 명령어를 차례대로 입력해주세요.\n!login MEMBERSHIP_ID PW\n!search START DEST MONTH DAY TIME(시)\n!select NUM```", inline=False)
    embed.add_field(name="!login 17123123 THISISPASSWD", value="코레일 사이트에 접속합니다. 성공적으로 로그인이 완료되면, 다음과 같은 메시지가 도착합니다. ```로그인이 완료되었습니다.```", inline=False)
    embed.add_field(name="!search 서울 춘천 1 13 1", value="표를 검색합니다. 성공적으로 검색이 완료되면, 다음과 같은 메시지가 도착합니다. ```구분\t열차번호\t출발\t도착\t가격\t소요시간\n0\t직통\t2027\t청량리19:15\t춘천20:20\t8,600원\t01:05\n1\t직통\t2029\t용산19:58\t춘천21:22\t9,800원\t01:24```", inline=False)
    embed.add_field(name="!select 0", value="선택한 표를 예약합니다. 성공적으로 취소표를 예약했다면 자동으로 장바구니에 추가되며, 다음과 같은 메시지가 도착한 뒤 봇이 종료됩니다.```장바구니에 담았습니다.\n봇을 종료합니다.```", inline=False)
    embed.set_footer(text="응답 메시지 도달에 시간이 오래 걸린다면, 누군가 봇을 사용 중이라는 뜻입니다. 조금만 기다리고 사용해주세요!")
    await ctx.send(embed=embed)

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
    print(ctx.message.author.name)
    await ctx.send(f'안녕하세요 {ctx.message.author.name}님! 봇이 정상적으로 작동중입니다.')


@bot.command()
async def reserve(ctx):
    username = str(ctx.message.author.name)
    print(f'[*] {username} : Reserving start')
    logger.warning(f'[*] {username} : Reserving start')
    work_list[username] = Korail()
    embed=discord.Embed(title="!reserve 명령어 성공", description="다음의 명령어를 차례대로 입력해주세요.\n```!login MEMBERSHIP_ID PW\n!search START DEST MONTH DAY TIME(시)\n!select NUM```", color=discord.Color.random())
    embed.set_author(name="ch4rli3kop", url="https://github.com/ch4rli3kop", icon_url="https://avatars.githubusercontent.com/u/35250476?s=400&u=b904844df4ef55a5dba52a232c70efc998372bf6&v=4")
    embed.set_footer(text="도움말은 `!help` 커맨드를 참고해주세요.")
    await ctx.send(embed=embed)

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
            login_success = work_list[ctx.message.author.name].korail_login(login_ID, login_PW)
            if login_success:
                embed=discord.Embed(title="!login 명령어 성공", description="로그인이 완료되었습니다. 다음 명령어를 입력해주세요. \nex) `!search 영등포 조치원 1 24 4`", color=discord.Color.random())
                embed.set_author(name="ch4rli3kop", url="https://github.com/ch4rli3kop", icon_url="https://avatars.githubusercontent.com/u/35250476?s=400&u=b904844df4ef55a5dba52a232c70efc998372bf6&v=4")
                embed.set_footer(text="도움말은 `!help` 커맨드를 참고해주세요.")
                await ctx.send(embed=embed)
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
            result = work_list[ctx.message.author.name].korail_search(start, dest, month, day, time)
        except:
            await ctx.send('실행오류.')
            return
        embed=discord.Embed(title="!search 명령어 성공", description="다음 리스트에서 예매할 기차표를 선택해주세요.\n**[주의] 20분 이내 열차는 예약할 수 없습니다.**\nex) `!select 0`", color=discord.Color.random())
        embed.set_author(name="ch4rli3kop", url="https://github.com/ch4rli3kop", icon_url="https://avatars.githubusercontent.com/u/35250476?s=400&u=b904844df4ef55a5dba52a232c70efc998372bf6&v=4")
        embed.set_footer(text="도움말은 `!help` 커맨드를 참고해주세요.")
        await ctx.send(embed=embed)
        await ctx.send(result)
        await ctx.send('20분 이내 열차는 예약할 수 없습니다.')

@bot.command()
async def select(ctx, *, text = None):
    if text != None:
        select = text.split(' ')[0]
        try:
            #  비동기 작업 추가
            task = asyncio.create_task(work_list[ctx.message.author.name].korail_reserve(select))
            result = await task
            if result:
                work_list[ctx.message.author.name].korail_quit()
                del work_list[ctx.message.author.name]
            else :
                await ctx.send('20분 이내의 열차는 예약하실 수 없습니다.\nsearch 단계부터 다시 해주세요.')
                return
        except RuntimeError as e:
            print(e)
            await ctx.send('인자를 확인해주세요.\nex)!select 3')
            return
        print(f'[*] {ctx.message.author.name} : Reserving finish')
        logger.warning(f'[*] {ctx.message.author.name} : Reserving finish')
        embed=discord.Embed(title="장바구니 추가 완료!", description="선택한 표를 장바구니에 추가했습니다.\n봇을 종료합니다.", color=discord.Color.random())
        embed.set_author(name="ch4rli3kop", url="https://github.com/ch4rli3kop", icon_url="https://avatars.githubusercontent.com/u/35250476?s=400&u=b904844df4ef55a5dba52a232c70efc998372bf6&v=4")
        embed.set_footer(text="도움말은 `!help` 커맨드를 참고해주세요.")
        await ctx.send(embed=embed)
    else:
        await ctx.send('인자를 확인해주세요.')

@bot.command()
async def whoisusing(ctx):
    await ctx.send(work_list)

bot.run(Token)
