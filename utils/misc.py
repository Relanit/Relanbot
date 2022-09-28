import re


def read_file(path):
    with open(path, encoding='utf8') as file:
        lines = file.readlines()
    return lines


def censore_banwords(text):
    with open('data/banwords.txt', 'r', encoding='utf-8') as f:
        banwords = [x for x in f.read().split('\n') if len(x) > 1]

    words = re.split(r'\W+', text)
    for word in words:
        for banword in banwords:
            if word.lower().find(banword) != -1:
                text = text.replace(word, '[УДАЛЕНО]')

    return text
