from asyncio.tasks import Task
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, timedelta
import pytesseract as tess
from discord import Status
#tess.pytesseract.tesseract_cmd = r".\dependencies\Tesseract-OCR\tesseract.exe"
from PIL import Image
import base64
import time
import sys
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
import json
import datetime
import pytz
import asyncio
DELAY = 5
TIMEOUT = 60
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


def get_link(string:str):
    begin = string.find("https://")
    string = string[begin:]
    string = string.splitlines()[0]
    return string

def getMeetingID(string:str):
    begin = string.find("Meeting ID")
    string = string[begin:]
    string = string.splitlines()[0]
    return string

def getPasscode(string:str):
    begin = string.find("Passcode")
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

intents = discord.Intents().all()

client = commands.Bot(command_prefix = get_prefix, help_command=None, intents=intents)

@client.event
async def on_ready():
    print("Bot is ready")
    if not test.is_running():
        test.start()    

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
            print(f"User {ctx.message.author.name} successfully registered")
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

    driver = webdriver.Chrome("./dependencies/chromedriver", options= chrome_options)
    
    try:

        with open("users.json", "r") as f:
            users = json.load(f)

        if str(ctx.author.id) in users:
            USER_ID = users[str(ctx.author.id)]["ID"]
            USER_PASS = users[str(ctx.author.id)]["PASS"]

            if USER_ID[0] == "<" and USER_ID[-1] == ">":
                print(f"{ctx.author.name} did the funni")
                await ctx.send("Try registering again but this time do not include <>. If you face any more difficulties feel free to contact <USER>")
                return

            if USER_PASS[0] == "<" and USER_PASS[-1] == ">":
                print(f"{ctx.author.name} did the funni")
                await ctx.send("Try registering again but this time do not include <>. If you face any more difficulties feel free to contact <USER>")
                return
            
        else:
            await ctx.send(f"No profile found for user {ctx.author.name}. Try using .register")
            print(f"{ctx.author.name} did not register and tried to use .schedule")
            return

        links = []

        driver.get("http://dpskolkata.net/")

        tries = 0

        logged_in = False
        while not logged_in and tries <= 10:
            try:

                wrong_captcha = driver.find_element_by_id("ContentPlaceHolder1_lblerr")
                
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

                img = Image.open("./captcha.jpg")
                captcha_text = tess.image_to_string(img).strip()


                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtCaptcha")))
                captcha_field = driver.find_element_by_id("ContentPlaceHolder1_txtCaptcha")
                captcha_field.send_keys(captcha_text)

                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_btnLogin")))
                login = driver.find_element_by_id("ContentPlaceHolder1_btnLogin")
                login.click()

                tries += 1
                
                print(tries)
            
            except:
                logged_in = True
            

        #login code
        
        #Send captcha to user to solve
            # await ctx.send("Type out the following captcha: ", file=discord.File("./captcha.jpg"))
            # os.remove("./captcha.jpg")

            # def check(message):
            #     return ctx.author.id == message.author.id

            # try:
            #     message = await client.wait_for("message", check=check, timeout=30)
            #     captcha_text = message.content
            # except TimeoutError:    
            #     await ctx.send("Request timed out") 
            #     return
                
        #Autosolve captcha with pytess
        try:
            wrong_captcha = driver.find_element_by_id("ContentPlaceHolder1_lblerr")
            await ctx.send("You have most probably registered with an invalid id and password. Try changing your credentials by using .unregister and then registering again!")
            print(f"{ctx.author.name} has mp registered with an invalid id or password")
            driver.quit()
            return
        except:
            print("Successfully logged in!")
            print(f"{ctx.author.name} logged in!")
            pass 



        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ContentPlaceHolder2_btnschedule")))
        schedule = driver.find_element_by_id("ContentPlaceHolder1_ContentPlaceHolder2_btnschedule")
        schedule.click()

        rows = driver.find_elements_by_xpath("//tbody/tr")

        if len(rows) == 0:
            await ctx.send(f"No schedule found for user {ctx.author.name}")
            print(f"No schedule found for user {ctx.author.name}")
            driver.quit()
            return

        embed=discord.Embed(title=f"Class links for {ctx.author.name}", color=0xff0000)

        for row in rows:
            segments = row.find_elements_by_xpath(".//td")
            if len(segments) != 0:
                embed.add_field(name = f"[{segments[-6].text}][{segments[-5].text}][{segments[-4].text}] ", value = f"Link: {get_link(segments[-3].text)}\n{getMeetingID(segments[-3].text)}\n{getPasscode(segments[-3].text)}\n\n", inline=False)

        # message = ""
        # for link in links:
        #     message += link
        #     message += "\n-------------------------------------------------------------------------------\n\n"
        # time.sleep(1)

        embed.set_footer(text="amogus sus")
        await ctx.send(embed=embed)
        print(f"{ctx.author.name} successfully recieved schedule!")
        driver.quit()
    except:
        driver.quit()
        await ctx.send("Something went wrong. Please contact <USER>")
        print(f"Something went wrong while trying to send schedule to {ctx.author.name}")

@tasks.loop(seconds=20)
async def test():

    current = datetime.datetime.now()

    if current.hour == 7 and current.minute < 2:

        with open("users.json", "r") as f:
            users = json.load(f)

        loop = asyncio.get_event_loop()
        tasks = []

        for user_id in users:
            task = loop.create_task(send_schedule(user_id, users[user_id]["ID"], users[user_id]["PASS"]))
            tasks.append(task)

        await asyncio.wait(tasks)

        return

@client.command()
async def help(ctx):
    embed=discord.Embed(title="SRM Fetcher Help", description="All the commands are to be used in the bot's DM", color=0xff0000)
    embed.add_field(name=".register", value="Used to register a new account to our network!", inline=False)
    embed.add_field(name=".unregister", value="Used to remove your account from our network", inline=False)
    embed.add_field(name=".schedule", value="Used to fetch your schedule from the SRM. This command can only be used after you have been registered to our network", inline=False)
    embed.add_field(name=".help", value="Displays this messagee", inline=False)
    embed.set_footer(text="amogus sus")
    await ctx.send(embed=embed)

@client.command()
async def sendall(ctx):

    with open("users.json", "r") as f:
        users = json.load(f)
    

    if ctx.message.author.id == '<your user id here>':
        await ctx.send("On it boss")

        loop = asyncio.get_event_loop()
        tasks = []

        for user_id in users:
            task = loop.create_task(send_schedule(user_id, users[user_id]["ID"], users[user_id]["PASS"]))
            tasks.append(task)
        
        await asyncio.wait(tasks)

async def send_schedule(user_id, id, password):

    try:
        user = await client.fetch_user(user_id)
        ctx = await user.create_dm()
        
        print(f"Sending to {user.name}")

        driver = webdriver.Chrome("./dependencies/chromedriver", options= chrome_options)

        USER_ID = id
        USER_PASS = password

        links = []

        driver.get("http://dpskolkata.net/")

        tries = 0

        logged_in = False
        while not logged_in and tries <= 10:
            try:

                wrong_captcha = driver.find_element_by_id("ContentPlaceHolder1_lblerr")
                
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

                img = Image.open("./captcha.jpg")
                captcha_text = tess.image_to_string(img).strip()


                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtCaptcha")))
                captcha_field = driver.find_element_by_id("ContentPlaceHolder1_txtCaptcha")
                captcha_field.send_keys(captcha_text)

                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_btnLogin")))
                login = driver.find_element_by_id("ContentPlaceHolder1_btnLogin")
                login.click()

                tries += 1
            
            except:
                logged_in = True
            
    #Autosolve captcha with pytess
        
        try:
            wrong_captcha = driver.find_element_by_id("ContentPlaceHolder1_lblerr")
            await ctx.send("You have most probably registered with an invalid id and password. Try changing your credentials by using .unregister and then registering again!")
            
            driver.quit()
            return
        except:
            
            pass    


        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ContentPlaceHolder2_btnschedule")))
        schedule = driver.find_element_by_id("ContentPlaceHolder1_ContentPlaceHolder2_btnschedule")
        schedule.click()

        rows = driver.find_elements_by_xpath("//tbody/tr")

        if len(rows) == 0:
            # await ctx.send(f"No schedule found for user {ctx.author.name}")
            print(f"No schedule found for {user.name}")
            driver.quit()
            return

        await asyncio.sleep(0.01)

        embed=discord.Embed(title=f"Class links for {user.name}", color=0xff0000)

        for row in rows:
            segments = row.find_elements_by_xpath(".//td")
            if len(segments) != 0:
                # embed.add_field(name = f"[{segments[-6].text}][{segments[-5].text}][{segments[-4].text}] Link: ", value = f"{get_link(segments[-3].text)}\n\n", inline=False)
                embed.add_field(name = f"[{segments[-6].text}][{segments[-5].text}][{segments[-4].text}] ", value = f"Link: {get_link(segments[-3].text)}\n{getMeetingID(segments[-3].text)}\n{getPasscode(segments[-3].text)}\n\n", inline=False)

        embed.set_footer(text="amogus sus")
        await ctx.send(embed=embed)
        print(f"Sent to {user.name}")
        driver.quit()
    except:
        driver.quit()
        print(f"Could not send to {user_id}")

@client.event
async def on_message(message):
    
    await client.process_commands(message)

    if message.author == client.user or message.author.bot:
        return
    elif not isinstance(message.channel, discord.DMChannel):
        return

    print(f"[{message.author.name}] >>'{message.content}'")

@client.event
async def on_command_error(ctx, error):
    print(f"{ctx.message.author}>>{error}")

client.run("TOKEN HERE")