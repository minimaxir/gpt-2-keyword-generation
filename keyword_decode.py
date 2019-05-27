import spacy
import csv
import re
from tqdm import tqdm
from itertools import chain
from random import random, shuffle


DELIMS = {
    'section': '~',
    'category': '`',
    'keywords': '^',
    'title': '@',
    'body': '}'
}


def build_pattern(sections):
    pattern_text = ''

    for section in section:
        pattern_text = DELIMS['section'] + DELIMS[section] + '(.*)'

    return re.compile(re.escape(pattern_text), flags=re.MULTILINE)


def keyword_decode(texts, input_sections=['keywords', 'titles'],
                   output_sections=['titles'],
                   pattern=None):

    # get the index of the group we want to extract
    group_indices = [i for i, section in enumerate(input_sections)
                     if section in output_sections]

    assert len(group_indices) > 0
    if pattern is None:
        pattern = build_pattern(input_sections)
    decoded_texts = []
    for text in texts:
        decoded_text = re.match(pattern, text)
        if decoded_text is None:
            continue
        decoded_text_attrs = (decoded_text.group(i) for i in group_indices)
        decoded_texts.append(decoded_text_attrs)
    return decoded_texts


def keyword_decode_file():


