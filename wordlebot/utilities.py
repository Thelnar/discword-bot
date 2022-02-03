import functools
import logging
import config as c
import os

os.makedirs(os.path.dirname(c.LOGGER_FOLDER), exist_ok=True)

wordle_logger = logging.getLogger('wordlebot')
wordle_logger.setLevel(logging.INFO)
my_handler = logging.FileHandler(filename=c.WORDLE_LOGGER_LOC, encoding='utf-8', mode='a')
my_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s'))
wordle_logger.addHandler(my_handler)

def alog(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        wordle_logger.info(f'{func.__name__} called with : {args} | {kwargs}')
        try:
            response = await func(*args, **kwargs)
            if response:
                wordle_logger.info(f'{func.__name__} returned {response}')
        except Exception as e:
            wordle_logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e
    return wrapper