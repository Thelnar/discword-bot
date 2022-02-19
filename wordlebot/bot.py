import logging
import discord
import os

import config as c
from commands import COMMAND_CODEX
from utilities import alog, wordle_logger

client = discord.Client()

# @alog
# async def closing_time():
#     await client.change_presence(status=discord.Status.invisible)
#     await client.close()
#     return "closed"


@client.event
@alog
async def on_ready():
    await client.change_presence(status=discord.Status.online)
    return f'Logged in as {client.user}'


@client.event
@alog
async def on_message(message):
    message_matters = (message.author != client.user) and \
                        (client.user in message.mentions or \
                        '<@&938244081727979580>' in message.content or \
                        message.channel.type == discord.ChannelType.private)
    if not message_matters:
        return f"Message didn't matter."
        # return f"""Message didn't matter:
        #             message_matters: {message_matters}, 
        #             author: {message.author}, 
        #             client: {client.user}, 
        #             mentions: {message.mentions},
        #             content: {message.content}"""
    wordle_logger.info(f'message received: {message.content} | from {message.author}')
    for regex, function in COMMAND_CODEX.items():
        match = regex.search(message.content)
        if match:
            await message.add_reaction(emoji='🤖')
            await function(client, message, match)
            return f'passed to {function.__name__}'
    await message.add_reaction(emoji='☠')

def main():
    os.makedirs(os.path.dirname(c.LOGGER_FOLDER), exist_ok=True)

    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.DEBUG)
    discord_handler = logging.FileHandler(filename=c.DISCORD_LOGGER_LOC, encoding='utf-8', mode='w')
    discord_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s'))
    discord_logger.addHandler(discord_handler)
    for _ in range(2):
        wordle_logger.info("")
    client.run(c.DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
