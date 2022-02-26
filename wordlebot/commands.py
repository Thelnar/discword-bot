import logging
import functools
import re
import discord
import datetime
import os
import sys

import config as c
from utilities import alog, wordle_logger
import game

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
                wordle_logger.exception(f"Exception: {str(e)}")
                raise e
        return wrapper
    return overwrapper


async def areact_reply(message, react=None, reply=None, reply_style=0):
    if react:
        await message.add_reaction(emoji=react)
    if reply:
        if reply_style == 0:
            await message.channel.send(reply)
        elif reply_style == 1:
            await message.reply(reply, mention_author=False)
        elif reply_style == 2:
            await message.reply(reply, mention_author=False)
    return "react: " + (react or '<None>') + f" reply style {reply_style}: " + (reply or '<None>')


@acodexed(re.compile(r'(^| +)((good(night|bye)|(?P<reset>res(et|tart)))([- ,.?!~_]|$))', flags=re.IGNORECASE))
@alog
async def func_closing_time(client, message, match):
    react = None
    reply = None
    #TODO user management system
    if message.author.id != c.DISCORD_OPERATOR_ID:
        react = '🙈'
        # reply = f'You are not authorized to do that, {message.author.mention}!'
    else:
        await client.change_presence(status=discord.Status.invisible)
        await client.close()
        if match.groupdict()['reset']:
            reply = "restarting client..."
            os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
        else:
            react = '😴'
            # reply = "I am sent to R'lyeh"
    return await areact_reply(message,react,reply)


@acodexed(re.compile(r'(^| )(?P<greeting>H(ello|i|ey|owdy))([- ,.?!~_]|$)', flags=re.IGNORECASE))
@alog
async def func_hello(client, message, match):
    react = None
    reply = f'{match.group("greeting")}, {message.author.mention}!'
    return await areact_reply(message,react,reply)

@acodexed(re.compile(r'^.*?(f.ck).*?(off)([- ,.?!~_]|$)'))
@alog
async def func_fuck_off(client, message, match):
    react = '🖕'
    reply = "Well, that was rude."
    return await areact_reply(message,react,reply)


@acodexed(re.compile(r"""
                    (?:^|[ ]+)play                                                                       # play command
                    (?:.*?                                           (?P<when>today|yesterday|[0-9]+))?  # when opt. arg
                    (?:.*?(?:strat)(?:egy)?[ ]*(?:=|:|of|is|[ ]*)[ ]*(?P<strategy>[a-z_]+))?             # strategy kwarg
                    .*?$""", flags=re.IGNORECASE|re.VERBOSE|re.DOTALL))
@alog
async def func_play_day(client, message, match):
    when = match.group('when') or 'Today'
    strat = match.group('strategy') or 'default'
    day_num = 0
    react = None
    reply = None
    if when[-1] in 'Yy':
        day_num = (datetime.date.today() - datetime.date.fromisoformat(c.WORDLE_DAY_ZERO)).days
        if when[0] in 'Yy':
            day_num -= 1
    else: 
        try:
            day_num = int(when)
        except ValueError as e:
            reply = "I didn't understand which day you wanted me to play"
    if not (-1 < day_num < len(c.WORDLE_ANSWERS)):
        reply = "that is an invalid day number."
    if reply == None:
        # reply = f"placeholder: day {day_num}, strat {strat}" #  wordle_it_out(c.WORDLE_ANSWERS[day_num], strat, c.DEFAULT_EMOJIS)
        game_answer = c.WORDLE_ANSWERS[day_num]
        game_result = game.play_wordle(game_answer,strat=game.STRAT_CODEX[strat])
        tries = 'X'
        if game_result[-1][0] == game_answer:
            tries = str(len(game_result))
        reply = f'Wordle {day_num} {tries}/6*\n\n'
        reply += game.log_to_text(game_result)
    return await areact_reply(message,react,reply)
