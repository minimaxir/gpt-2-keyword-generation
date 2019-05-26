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

PRONOUNS = set(['i', 'me', 'we', 'you', 'he', 'she',
                'it', 'him', 'her', 'them', 'they'])


def build_section(section, text):
    if text is None:
        return ''
    return DELIMS['section'] + DELIMS[section] + text


def encode_keywords(csv_path, model='en_core_web_sm',
                    category_field=None,
                    keywords_field=None,
                    title_field=None,
                    body_field=None,
                    keyword_gen='title',
                    keyword_sep=',',
                    dropout=0.5,
                    repeat=3,
                    max_keywords=3,
                    keyword_length_max=20,
                    out_path='csv_encoded.txt',
                    start_token="<|startoftext|>",
                    end_token="<|endoftext|>"):

    nlp = spacy.load(model)
    pattern = re.compile('\W+')

    # Count the number of rows to set up progress bar
    # Adapted from https://stackoverflow.com/a/19001475

    with open(csv_path, 'r', encoding='utf8', errors='ignore') as f:
        reader = csv.DictReader(f)
        num_rows = sum(1 for _ in reader)

    with open(csv_path, 'r', encoding='utf8', errors='ignore') as f:
        with open(out_path, 'w', encoding='utf8', errors='ignore') as w:
            reader = csv.DictReader(f)
            for row in tqdm(reader, total=num_rows):

                # category should be normalized to account for user input
                category = re.sub(pattern, '-', row[category_field].lower().strip()) if category_field is not None else None

                title = row[title_field] if title_field is not None else None
                body = row[body_field] if body_field is not None else None

                if keywords_field is None:
                    # Generate the keywords using spacy
                    doc = nlp(row[keyword_gen])
                    keywords = [[chunk.text, chunk.root.text]
                                for chunk in doc.noun_chunks]
                    keywords = [re.sub(pattern, '-', text.lower())
                                for text in chain.from_iterable(keywords)
                                if len(text) <= keyword_length_max]
                else:
                    keywords = [re.sub(pattern, '-', keyword.lower().strip())
                                for keyword in row[keyword_gen].split(keyword_sep)]

                keywords = set(keywords) - PRONOUNS   # dedupe + remove pronouns

                for _ in range(repeat):
                    new_keywords = [keyword for keyword in keywords
                                    if random() < dropout]
                    shuffle(new_keywords)
                    new_keywords = " ".join(new_keywords[:max_keywords])

                    w.write(start_token +
                            build_section('category', category) +
                            build_section('keywords', new_keywords) +
                            build_section('title', title) +
                            build_section('body', body) +
                            end_token + "\n")
