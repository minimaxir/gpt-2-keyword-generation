import spacy
import csv
import re
from random import random, shuffle


delims = {
    'category': '`',
    'keywords': '^',
    'title': '@',
    'body': '}'
}


def build_section(section_delim, section, text):
    if text is None:
        return ''
    if section == 'keywords':
        text = " ".join(text)
    return section_delim + delims[section] + text


def encode_keywords(csv_path, model='en_core_web_sm',
                    category_field=None,
                    keywords_field=None,
                    title_field=None,
                    body_field=None,
                    keyword_gen='title',
                    keyword_sep=',',
                    section_delim='~',
                    dropout=0.5,
                    repeat=3,
                    max_keywords=3,
                    out_path='csv_encoded.txt',
                    start_token="<|startoftext|>",
                    end_token="<|endoftext|>"):

    nlp = spacy.load(model)
    pattern = re.compile('\W+')

    with open(csv_path, 'r', encoding='utf8', errors='ignore') as f:
        with open(out_path, 'w', encoding='utf8', errors='ignore') as w:
            reader = csv.DictReader(f)
            for row in reader:

                # category should be normalized to account for user input
                category = re.sub(pattern, '-', row[category_field].lower().strip()) if category_field is not None else None

                title = row[title_field] if title_field is not None else None
                body = row[body_field] if body_field is not None else None

                if keywords_field is None:
                    # Generate the keywords using spacy
                    doc = nlp(row[keyword_gen])
                    keywords = [re.sub(pattern, '-', chunk.text.lower())
                                for chunk in doc.noun_chunks]
                else:
                    keywords = [re.sub(pattern, '-', keyword.lower().strip())
                                for keyword in row[keyword_gen].split(keyword_sep)]

                for _ in repeat:
                    new_keywords = [keyword for keyword in keywords
                                    if random < dropout]
                    shuffle(new_keywords)
                    new_keywords = new_keywords[:max_keywords]

                    w.write(start_token +
                            build_section(section_delim, 'category', category) +
                            build_section(section_delim, 'keywords', keywords) +
                            build_section(section_delim, 'title', title) +
                            build_section(section_delim, 'body', body) +
                            end_token + "\n")
