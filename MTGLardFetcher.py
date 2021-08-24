#!/usr/bin/env python

from discord import *
import praw
import re
import sys
import time
import random
#import sqlite3
import os
from tendo import singleton
import sys
import pprint
import importlib


importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

persistence = True

def get_matches(text):
    matches = re.findall(r'\[\[([^\[\]]*?)\]\]', text)
    #matches = re.findall(r'\[\[(.*?)\]\]', text)
    return matches

def get_links(r):
    #subreddit = r.get_subreddit('MTGLardFetcher')
    subreddit = r.subreddit('MTGLardFetcher')
    candidates = ['http://i.imgur.com/66Knlyo.png'] # pot of greed is always an option
    #candidates = ['https://i.redd.it/4f1qxxl3dqc21.png'] # bleep bleep
    for post in subreddit.hot(limit=50):
        if not "/r/MTGLardFetcher" in post.url:
            # allow only serious domains 
            if re.search('(i.redd.it|i.imgur.com)', post.url):
                candidates.append(post.url)
                print("cool domain approved by MARO", post.url)
            else:
                print("shitty domain excluded by speculators", post.url)

    print("refreshed candidate list:")
    for c in candidates:
        print(c)

    return candidates        
        

async def bot_action(c, matches, links, channel):
    act = False
    for m in matches:
        act = True
        #print m
        link = random.choice(links)
        embed = Embed(title = " - [" +m+ "]", url=link)
        embed.set_image(url=link)
        await channel.send(embed = embed)


    text = """If WotC didn't do anything wrong this week, 
            you can rage at this bot instead at
            https://reddit.com/r/MTGLardFetcher or, even submit some of 
            the sweet Siege Rhino alters your GF made\n"""
    if act:
        await channel.send(embed=Embed(title="^(Probably totally what you linked)\n\n", description=text, url="https://reddit.com/r/MTGLardFetcher"))
    

class MyClient(Client):
    def __init__(self, c, links):
        super().__init__()
        self.c = c
        self.links = links
        self.last_refresh = 0
    
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, ctx):
        now = int(time.time()) 
        if (now - self.last_refresh > 60):            
            self.last_refresh = now
            self.links = get_links(r)
            
        if not ctx.author.bot:
            await bot_action(self.c, get_matches(ctx.content), self.links, ctx.channel)


if __name__ == '__main__':

    me = singleton.SingleInstance()

    UA = 'MTGLardFetcher, a MTGCardFetcher Parody bot for /r/magicthecirclejerking. Kindly direct complaints to /u/0x2a'
    #r = praw.Reddit(UA)

    r = praw.Reddit( user_agent=UA, 
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            refresh_token=os.getenv('REFRESH_TOKEN')
            )
    

    last_refresh = int(time.time())
    links = get_links(r)
    
    client = MyClient(r, links)
    client.run(os.getenv('TOKEN'))
