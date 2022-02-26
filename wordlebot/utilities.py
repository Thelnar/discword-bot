import functools
import logging
import config as c
import os
import pickle


os.makedirs(os.path.dirname(c.LOGGER_FOLDER), exist_ok=True)

wordle_logger = logging.getLogger('wordlebot')
wordle_logger.setLevel(logging.INFO)
my_handler = logging.FileHandler(filename=c.WORDLE_LOGGER_LOC, encoding='utf-8', mode='a')
my_handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(filename)s : %(funcName)s : %(message)s')) # https://docs.python.org/3/library/logging.html#logrecord-attributes
wordle_logger.addHandler(my_handler)

def alog(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        wordle_logger.info(f'called with {args} | {kwargs}')
        try:
            response = await func(*args, **kwargs)
            if response:
                wordle_logger.info(f'returned {response}')
        except Exception as e:
            wordle_logger.exception(f"Exception: {str(e)}")
            raise e
    return wrapper

# async def apickle(filename):
    
#     def overwrapper(func):
        
#         @functools.wraps(func)
#         async def wrapper(*args, **kwargs):
#             try:
#                 await func(*args, **kwargs)
#             except Exception as e:
#                 wordle_logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
#                 raise e
#         return wrapper

#     return overwrapper