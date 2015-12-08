import re
import time
import os
import subprocess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def tokenize(text):
    return re.findall(r'[\w]+', text)


def get_ngrams(words, order, sep=' '):
    return [sep.join(words[n - order: n]) for n in range(order, len(words)+1)]


def avg(values):
    return sum(values)/len(values)


def note_the_time(name="Something"):
    def wrap(f):
        def wrapper(*args, **kwargs):
            begin = time.time()
            fn = f(*args, **kwargs)
            end = time.time()
            print("[%s is finished in %.2f]" % (name, end - begin))
            return fn
        return wrapper
    return wrap


def execute_mystem(tokens):
    env = os.environ.copy()
    env['PATH'] = ":".join((env['PATH'], '/Users/bor1ng/Applications'))
    p = subprocess.Popen(
        "mystem -i --format json", stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, shell=True, env=env)
    output, err = p.communicate(tokens)
    return output, err


def get_pos(token, not_recognized=None):
    if token['analysis']:
        return re.findall(r'[A-Z]+', token['analysis'][0]['gr'])[0]
    else:
        return not_recognized