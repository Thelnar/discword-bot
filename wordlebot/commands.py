import logging
import functools
import re
import discord
import datetime

import config as c
from utilities import alog, wordle_logger

COMMAND_CODEX = {}
#     re.compile('(^| )(?P<greeting>H(ello|i|ey|owdy))([- ,.?!~_]|$)', flags=re.IGNORECASE) : func_hello,
#     re.compile('good(night|bye)', flags=re.IGNORECASE) : func_closing_time,
#     re.compile('', flags=re.IGNORECASE): func_play_day,
#     re.compile('(^| )(play today) *(s(trat)?(egy)?=(?P<strategy>[.+?]))? *(h(ard)?m(ode)?=(?<hardmode>(t(rue)?|f(alse)?)))?', flags=re.IGNORECASE): func_play_today
# }

def acodexed(pattern):
    def overwrapper(func):
        COMMAND_CODEX[pattern] = func
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except Exception as e:
                wordle_logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper
    return overwrapper


@acodexed(re.compile('(^| +)good(night|bye)([- ,.?!~_]|$)', flags=re.IGNORECASE))
@alog
async def func_closing_time(client, message, match):
    #TODO user management system
    if message.author.id != c.DISCORD_OPERATOR_ID:
        response = f'You are not authorized to do that, {message.author.mention}!'
        await message.channel.send(response)
        return response
    # await message.channel.send("I am sent to R'lyeh")
    await client.change_presence(status=discord.Status.invisible)
    await client.close()
    return "closed"


@acodexed(re.compile('(^| )(?P<greeting>H(ello|i|ey|owdy))([- ,.?!~_]|$)', flags=re.IGNORECASE))
@alog
async def func_hello(client, message, match):
    response = f'{match.group("greeting")}, {message.author.mention}!'
    await message.channel.send(response)
    return response

@acodexed(re.compile(r"""
                    (^|[ ]+)play                                                                        # play command
                    ([ ]+the)?([ ]+wordle)?([ ]+from)?([ ]+day)?([ ]+number)?([ ]+\#)?[ ]*              # optional English words
                    ((w)?(hen)?    [ ]*(=|:|[ ]*|of|is)[ ]*(?P<when>(today|yesterday|[0-9]+)))?.*?      # when kwarg
                    (s(trat)?(egy)?[ ]*(=|:|[ ]*|of|is)[ ]*(?P<strategy>[a-z_]+))?.*?                   # strategy kwarg
                    # (h(ard)?m(ode)?[ ]*(=|:|[ ]+|of|is)[ ]*(?P<hardmode>(t(rue)?|f(alse)?|on|off)))?  # hardmode kwarg
                    """, flags=re.IGNORECASE|re.VERBOSE|re.DOTALL))
@alog
async def func_play_day(client, message, match):
    when = match.group('when') or 'Today'
    strat = match.group('strategy') or 'default'
    day_num = 0
    response = ""
    if when[-1] in 'Yy':
        day_num = (datetime.date.today() - datetime.date.fromisoformat(c.WORDLE_DAY_ZERO)).days
        if when[0] in 'Yy':
            day_num -= 1
    else:
        try:
            day_num = int(when)
        except ValueError as e:
            response = "I didn't understand which day you wanted me to play"
    if not (-1 < day_num < len(c.WORDLE_ANSWERS)):
        response = "that is an invalid day number."
    if response == "":
        response = f"placeholder: day {day_num}, strat {strat}" #  wordle_it_out(c.WORDLE_ANSWERS[day_num], strat, c.DEFAULT_EMOJIS)
    await message.channel.send(response)
    return response
