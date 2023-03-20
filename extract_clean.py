import re
from dateutil import parser
import json
import codecs
from bs4 import BeautifulSoup


def clean(text):
    # clear special characters that don't want
    clean = re.compile('<.*?>|&nbsp;')
    text = re.sub(clean, '', str(text))

    # remove bottom part that not have data
    pattern = re.compile("Attention")
    match = pattern.search(text)
    start = match.start()
    # end = match.end()

    # Remove the text after the match
    text = text[:start]
    return text


def print_data(text, data):
    print(text + " : " + str(data))


def cut_text(text, start, end):
    pattern = re.compile(str(start))
    match = pattern.search(text)
    start = match.start()
    if end != 0:
        pattern = re.compile(str(end))
        match = pattern.search(text)
        end = match.start()
        new_text = text[start:end]
        return new_text

    new_text = text[start:]
    return new_text


def text_to_array(pattern, text):
    text = re.split(pattern, text)
    while '' in text:
        text.remove('')
    return text
