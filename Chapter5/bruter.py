import queue
import requests
import threading
import sys

AGENT = "Mozila/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
EXTENTIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = "https://ssystems.ir/"
THREADS = 50
WORDLIST = "/home/kalafe/bhp/SVNDigger-1/all.txt"

def get_words(resume=None):

    def extend_words(word):
        if "." in word:
            words.put(f'/{word}')
        else:
            words.put(f'/{word}/')
        for extention in EXTENTIONS:
            words.put(f'/{word}{extention}')
        
    with open(WORDLIST) as f:
        raw_words = f.read()
        
    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f'Resuming wordlist from: {resume}')
        else: 
            print(word)
            extend_words(word)
    return words

def dir_brute(words):
    headers = {'User-Agent': AGENT}
    while not words.empty():
        url = f'{TARGET}{words.get()}'
        try:
            r = requests.get(url=url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stderr.write('X');sys.stderr.flush()
            continue
        
        if r.status_code == 200:
            print(f'\n Success ({r.status_code}: {url})')
        elif r.status_code == 404:
            sys.stderr.write('.');sys.stderr.flush()
        else:
            print(f'{r.status_code} => {url}')

if __name__ == '__main__':
    words = get_words()
    print('Press return to continue.')
    sys.stdin.readline()
    for _ in range(THREADS):
        t = threading.Thread(target=dir_brute, args=(words,))
        t.start()