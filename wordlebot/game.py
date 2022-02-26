from ast import Pass
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
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                wordle_logger.exception(f"Exception: {str(e)}")
                raise e
        return wrapper
    return overwrapper

def log_to_text(guess_log, emoji_map=None):
    text = ''
    if emoji_map is None:
        emoji_map = {'0' : u'\u2B1C', # Large White Square
                     '1' : u'\U0001F7E8', # Large Yellow Square
                     '2' : u'\U0001F7E9',} # Large Green Square
    for entry in guess_log:
        text += ''.join([emoji_map[char] for char in entry[1]])
        text += '||' + ' ' * random.randrange(0,4) + entry[0] + ' ' * random.randrange(0,4) + '||\n'
    return text


def make_cover(guess, answer):
    answer = answer.ljust(len(guess))
    guess, answer = zip(*[('`','`') if g == a else (g,a) for g,a in zip(guess, answer)])
    cover = ['2' if g == answer[i] else str(int( guess[:i+1].count(g) <= answer.count(g) )) for i,g in enumerate(guess)]
    return ''.join(cover)

def curry_is_possible(facts, min_len, max_len):
    letter_mask = f'(?i)^(?=(?:.){{{min_len},{max_len}}}$)' # (?:.*)$'
    all_ins = [None for _ in range(max_len)]
    all_outs = [set() for _ in range(max_len)]
    for letter,info in facts.items():
        letter_mask += f"(?=(?:[^{letter}]*?{letter}){{{info['min']},{info['max']}}}[^{letter}]*?$)"
        for loc in info['ins']:
            if not all_ins[loc]:
                all_ins[loc] = letter
            else:
                wordle_logger.critical(f'Multiple letters in same position! {all_ins[loc]}, {letter}')
        for loc in info['outs']:
            all_outs[loc].add(letter)
    lookslike = [found or ('[^' + ''.join(outs) + ']' if len(outs) > 0 else '.') for found,outs in zip(all_ins,all_outs)]
    letter_mask += ''.join(lookslike) + '$'
    mask = re.compile(letter_mask)
    def is_possible(word):
        return not not mask.match(word.ljust(max_len))
    return is_possible


def get_possibilities(guess_log, min_len, max_len, lexicon):
    # letter_mask = ['[^`]' for _ in range(max_len)]
    # letter_mask = ['^(?i)'] + letter_mask + ['$']
    facts = {}
    fact = {'min' : 0,
            'max' : max_len,
            'ins' : None,
            'outs' : None}
    for entry in guess_log:
        guess = entry[0]
        cover = entry[1]
        for i in range(len(guess)):
            if guess[i] not in facts:
                facts[guess[i]] = fact.copy()
                facts[guess[i]]['ins'] = set() # Assign here rather than in fact definition due to .copy being a "shallow" copy
                facts[guess[i]]['outs'] = set() # This way avoids these pointers pointing to the same set
            if cover[i] == '0':
                facts[guess[i]]['max'] = min(facts[guess[i]]['max'],sum([g==guess[i] for g,v in zip(guess,cover) if v != '0']))
            else:
                facts[guess[i]]['min'] = max(facts[guess[i]]['min'], sum([g==guess[i] for g,v in zip(guess,cover) if v != '0']))
                if cover[i] == '2':
                    facts[guess[i]]['ins'].add(i)
                elif cover[i] == '1':
                    facts[guess[i]]['outs'].add(i)
                else:
                    wordle_logger.exception(f'Malformed Cover Detected: {cover}\n{guess_log}\n{min_len}\n{max_len}')
            if False:
                # j = i + 1
                # if cover[i] == '2':
                # if cover[i] == '0':
                #     num_to_have = sum(g == guess[i] and v != '0' for g,v in zip(guess, cover))
                #     if num_to_have == 0:
                #         letter_mask = letter_mask[:1] + [letter_mask[k][:2] + guess[i] + letter_mask[k][2:] \
                #                                         if letter_mask[k][0] == '[' and \
                #                                         guess[i] not in letter_mask[k] else letter_mask[k] \
                #                                         for k in range(1,len(letter_mask))]
                #     else:
                #         letter_mask[0] = letter_mask[0] + f'(?=(.*{guess[i]}){{{num_to_have}}})'
                #         if letter_mask[j][0] == '[' and guess[i] not in letter_mask[j]:
                #             letter_mask[j] = letter_mask[j][:2] + guess[i] + letter_mask[j][2:]
                # elif cover[i] == '1':
                #     letter_mask[0] = letter_mask[0] + f'(?=.*{guess[i]})'
                #     if letter_mask[j][0] == '[' and guess[i] not in letter_mask[j]:
                #         letter_mask[j] = letter_mask[j][:2] + guess[i] + letter_mask[j][2:]
                # elif cover[i] == '2':
                #     letter_mask[j] = guess[i]
                pass
    is_possible = curry_is_possible(facts, min_len, max_len)
    possibilities = [word for word in lexicon if is_possible(word)]
    if possibilities == []:
        wordle_logger.exception(f"failed to find any possibilities")
        raise IndexError
    return possibilities

@strat_dexed('default','rp')
def random_possibility(answer, guess_log, min_len, max_len, lexicon):
    possibilities = get_possibilities(guess_log, min_len, max_len, lexicon)
    guess = random.choice(possibilities)
    cover = make_cover(guess, answer)
    return (guess, cover)

def play_wordle(answer, strat=random_possibility, num_tries=6, min_len=5, max_len=5, lexicon=c.WORDLE_LEXICON):
    answer = answer.ljust(max_len)
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
        print(play_wordle('bowls'))
