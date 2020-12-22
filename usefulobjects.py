import random
import discord
import yaml

config = yaml.safe_load("config.yml")

def simplebed(title,text):
    embedvar = discord.Embed(title=title,description=text,color=config['basecolor'])
    return embedvar
