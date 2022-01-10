import discord
from discord.ext import commands
from bot_token import Token

bot=commands.Bot(command_prefix='!')

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
    await ctx.send('안녕하세요')

@bot.command()
async def hihi(ctx, *, text = None):
    print(text)
    if text != None:
        await ctx.send(text)
    else:
        await ctx.send('인자를 확인해주세요')

bot.run(Token)