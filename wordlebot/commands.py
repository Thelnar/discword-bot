import logging
import functools
import re

my_logger = logging.getLogger('commands')
my_logger.setLevel(logging.INFO)
my_handler = logging.FileHandler(filename='commands.log', encoding='utf-8', mode='w')
my_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s'))
my_logger.addHandler(my_handler)

def log(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        my_logger.info(f'{func.__name__} called with : {args} | {kwargs}')
        try:
            await func(*args, **kwargs)
        except Exception as e:
            my_logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e
    return wrapper


@log
async def func_hello(match, message):
    response = f'{match.group("greeting")}, {message.author.mention}!'
    await message.channel.send(response)
    my_logger.info(response)


@log
async def play_day(match, message):
    pass


command_codex = {
    re.compile('(^| )(?P<greeting>H(ello|i|ey|owdy))([- ,.?!~_]|$)', flags=re.IGNORECASE) : func_hello
}
