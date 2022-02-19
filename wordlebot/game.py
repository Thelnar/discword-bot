import config as c
import random
import re
import functools
from english_words import english_words_lower_set

from utilities import wordle_logger
# guess_log_example = [('guess','cover')]

STRAT_CODEX = {}

def strat_dexed(*args):
    def overwrapper(func):
        for arg in args:
            STRAT_CODEX[arg] = func
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except Exception as e:
                wordle_logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper
    return overwrapper

def log_to_text(guess_log, emoji_map=None):
    text = ''
    if emoji_map is None:
        emoji_map = {'0' : u'\u2B1C', # Large White Square
                     '1' : u'\1F7E8', # Large Yellow Square
                     '2' : u'\1F7E9',} # Large Green Square
    for entry in guess_log:
        text += ''.join([emoji_map[char] for char in entry[1]])
        text += '||' + entry[0] + '||\n'
    return log_to_text


def make_cover(guess, answer):
    answer = answer.ljust(len(guess))
    guess, answer = zip(*[('`','`') if g == a else (g,a) for g,a in zip(guess, answer)])
    cover = ['2' if g == answer[i] else str(int( guess[:i+1].count(g) <= answer.count(g) )) for i,g in enumerate(guess)]
    return ''.join(cover)

def curry_is_possible(letter_mask, min_len):
    def is_possible(word):
        long_enough = len(word) >= min_len
        matches_mask = re.match('(?i)' + letter_mask,word.ljust(len(letter_mask))) # case-insensitive regex match
        return long_enough and matches_mask
    return is_possible

def get_possibilities(guess_log, min_len, max_len, lexicon):
    possibilities = []
    letter_mask = ['[^`]' for _ in range(max_len)]
    letter_mask = ['(?=.*)'] + letter_mask
    for entry in guess_log:
        guess = entry[0]
        cover = entry[1]
        for i in range(len(guess)):
            if cover[i] == '0':
                letter_mask = [letter_mask[i+1][:2] + guess[i] + letter_mask[i+1][2:] \
                               if letter_mask[i+1] == '[' else letter_mask[i+1] \
                               for i in range(len(letter_mask))]
            elif cover[i] == '1':
                letter_mask[0] = letter_mask[0] + f'(?=.*{guess[i]})'
                if letter_mask[i][0] == '[':
                    letter_mask[i] = letter_mask[i+1][:2] + guess[i] + letter_mask[i+1][2:]
            elif cover[i] == '2':
                letter_mask[i+1] = guess[i]
    is_possible = curry_is_possible(''.join(letter_mask), min_len)
    possibilities = [word for word in lexicon if is_possible(word)]
    if possibilities == []:
        wordle_logger.exception(f"get_possibilities failed to find any possibilities")
    return possibilities

@strat_dexed('default','rp')
def random_possibility(answer, guess_log, min_len, max_len, lexicon):
    possibilities = get_possibilities(guess_log, min_len, max_len, lexicon)
    guess = random.choice(possibilities)
    cover = make_cover(guess, answer)
    return (guess, cover)

def play_wordle(answer, strat=random_possibility, num_tries=6, min_len=5, max_len=5, lexicon=c.WORDLE_LEXICON):
    guess_log = []
    for i in range(num_tries):
        guess = strat(answer, guess_log, min_len, max_len, lexicon)
        guess_log.append(guess)
        if guess[0] == answer:
            break
    return guess_log

if __name__ == '__main__':
    # get_possibilities([('cetes', '20000'), ('chica', '20100')],5,5,c.WORDLE_LEXICON)
    for i in range(10):
        print(play_wordle('cynic'))
