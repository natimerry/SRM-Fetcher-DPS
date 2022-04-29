# this shit is written by Atendimento2005 harass him for issues
# fuck propiertary software
# #FOSSGang
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, timedelta
import pytesseract as tess
from PIL import Image
import base64
import time
import sys
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
import json
import requests
import keep_alive
 
DELAY = 5
TIMEOUT = 60
 
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument("--headless")
# chrome_options.add_argument("--profile-directory=.\data\Default")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
 
def get_link(string:str):
    begin = string.find("https://")
    string = string[begin:]
    string = string.splitlines()[0]
    return string
 
 
def get_prefix(client, message):
    if not message.guild:
        return commands.when_mentioned_or(".")(client, message)
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
 
    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or(".")(client, message)
 
    prefix = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(prefix)(client, message)
 
client = commands.Bot(command_prefix = get_prefix)
 
@client.event
async def on_ready():
    print("Bot is ready")
 
@client.command()
async def ping(ctx):
    await ctx.send(f"Ping! {round(client.latency*1000)}ms")
 
@client.command()
async def prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
 
    prefixes[str(ctx.guild.id)] = prefix
 
    await ctx.send(f'Set the server prefix to {prefix}')
 
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent = 4)
 
@client.command()
async def register(ctx, admnno, password):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        with open("users.json", "r") as f:
            users = json.load(f)
    
        if str(ctx.author.id) in users.keys():
            await ctx.send(f"You already have a profile registered with:-\nAdmission no.: {users[str(ctx.author.id)]['ID']} \nPassword: {users[str(ctx.author.id)]['PASS']}\nYou can try using .unregister to remove your current details and then try using this command again.")
        else:
            users[ctx.author.id] = {"ID": admnno, "PASS": password} 
 
            with open("users.json", "w") as f:
                json.dump(users, f, indent = 4)
 
            await ctx.send(f"User {ctx.message.author.name} successfully registered with Admission number: {admnno} and Password: {password}")
    else:
        await ctx.message.delete()
        await ctx.send("The command you just ran put your login details at risk and thus we have deleted the message. Try DMing your command to me for it to work as intended")
 
    # await ctx.send("okLol")
@register.error
async def register_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Usage: .register <admission no.> <password>")
 
@client.command()
async def unregister(ctx):
    with open("users.json", "r") as f:
        users = json.load(f)
 
    if str(ctx.author.id) in users:
        del users[str(ctx.author.id)]
        await ctx.send(f"Credentials erased successfully for {ctx.author.name}")
    else:
        await ctx.send(f"No credentials found for {ctx.author.name}. Try registering first with .register")
 
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)
 
@client.command()
async def schedule(ctx):    
    driver = webdriver.Chrome(options= chrome_options)
    
    with open("users.json", "r") as f:
        users = json.load(f)
 
    if str(ctx.author.id) in users:
        USER_ID = users[str(ctx.author.id)]["ID"]
        USER_PASS = users[str(ctx.author.id)]["PASS"]
    else:
        await ctx.send(f"No profile found for user {ctx.author.name}. Try using .register")
        return
 
    links = []
 
    driver.get("http://dpskolkata.net/")
 
    #login code
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtusername")))
    username = driver.find_element_by_id("ContentPlaceHolder1_txtusername")
    username.send_keys(Keys.CONTROL + "A", Keys.BACKSPACE)
    username.send_keys(USER_ID)
 
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtpwd")))
    password = driver.find_element_by_id("ContentPlaceHolder1_txtpwd")
    password.send_keys(Keys.CONTROL + "A", Keys.BACKSPACE)
    password.send_keys(USER_PASS)
 
 
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_imgCaptcha")))
    captcha = driver.find_element_by_id("ContentPlaceHolder1_imgCaptcha")
    src = captcha.get_attribute("src")        
 
    img_captcha_base64 = driver.execute_async_script("""
    var ele = arguments[0], callback = arguments[1];
    ele.addEventListener('load', function fn(){
    ele.removeEventListener('load', fn, false);
    var cnv = document.createElement('canvas');
    cnv.width = this.width; cnv.height = this.height;
    cnv.getContext('2d').drawImage(this, 0, 0);
    callback(cnv.toDataURL('image/jpeg').substring(22));
    }, false);
    ele.dispatchEvent(new Event('load'));
    """, captcha)
 
    with open(r"captcha.jpg", 'wb') as f:
        f.write(base64.b64decode(img_captcha_base64))
    
 
    await ctx.send("Type out the following captcha: ", file=discord.File("./captcha.jpg"))
    os.remove("./captcha.jpg")
 
 
    try:
        def check(message):
            return ctx.author.id == message.author.id
            
        message = await client.wait_for("message", check=check, timeout=30)
        captcha_text = message.content
    except TimeoutError:    
        await ctx.send("Request timed out") 
        driver.quit()
        return
        
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtCaptcha")))
    captcha_field = driver.find_element_by_id("ContentPlaceHolder1_txtCaptcha")
    captcha_field.send_keys(captcha_text)
 
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_btnLogin")))
    login = driver.find_element_by_id("ContentPlaceHolder1_btnLogin")
    login.click()
 
    try:
        wrong_captcha = driver.find_element_by_id("ContentPlaceHolder1_lblerr")
    except:
        await ctx.send("Invalid Captcha!")
        driver.quit()
        return
 
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ContentPlaceHolder2_btnschedule")))
    schedule = driver.find_element_by_id("ContentPlaceHolder1_ContentPlaceHolder2_btnschedule")
    schedule.click()
 
    rows = driver.find_elements_by_xpath("//tbody/tr")
    for row in rows:
        segments = row.find_elements_by_xpath(".//td")
        if len(segments) != 0:
            link = f"[{segments[-6].text}][{segments[-5].text}][{segments[-4].text}] Link: {get_link(segments[-3].text)}\n"
            links.append(link)
    
    driver.quit()
 
    message = ""
    for link in links:
        message += link
        message += "\n---------------------------------------------------------------------------------------------\n\n"
    time.sleep(1)
 
    print(message)
 
    if message == "":
        await ctx.send(f"No schedule found for user {ctx.author.name}")
        return
 
    await ctx.send(message)
keep_alive.keep_alive()
