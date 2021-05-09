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

DELAY = 5
TIMEOUT = 60

chrome_options = Options()
chrome_options.add_argument('--log-level=3')
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--user-data-dir=D:\One for All\PyProjects\ScheduleGrabber\data")
# chrome_options.add_argument("--profile-directory=.\data\Default")
chrome_options.add_argument('--profile-directory=Debug')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options= chrome_options)

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
    with open("users.json", "r") as f:
        users = json.load(f)

    

client.run("ODQwNTQ1MjY1ODg2NjkxMzMw.YJZwxw.OdIeTWco4zMW1Tqs1rlADwljYFE")
