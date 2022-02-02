import logging
import discord

import config as c
from commands import command_codex

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)
discord_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
discord_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s'))
discord_logger.addHandler(discord_handler)

my_logger = logging.getLogger('bot')
my_logger.setLevel(logging.INFO)
my_handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
my_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s'))
my_logger.addHandler(my_handler)

client = discord.Client()

@client.event
async def on_ready():
    my_logger.info(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    message_matters = False
    message_matters = (message.author != client.user) and (client.user in message.mentions)
    if not message_matters:
        return
    my_logger.info(f'message received: {message.content} | from {message.author}')
    for regex, function in command_codex.items():
        match = regex.search(message.content)
        if match:
            await message.add_reaction(emoji='🤖')
            await function(match, message)
            return
    await message.add_reaction(emoji='☠')

client.run(c.DISCORD_BOT_TOKEN)
