import spacy
import csv
import re
import ray
import multiprocessing
from functools import partial
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

    data_list = []

    with open(csv_path, 'r', encoding='utf8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_list.append(row)

    shuffle(data_list)

    # https://stackoverflow.com/a/434328
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    num_threads = multiprocessing.cpu_count() * 2   # colocate 2 processes per thread
    encoders = [Encoder.remote(model, category_field,
                               keywords_field,
                               title_field,
                               body_field,
                               keyword_gen,
                               keyword_sep,
                               dropout,
                               repeat,
                               max_keywords,
                               keyword_length_max,
                               start_token,
                               end_token,
                               DELIMS,
                               PRONOUNS) for _ in range(num_threads)]

    with open(out_path, 'w', encoding='utf8', errors='ignore') as w:
        pbar = tqdm(total=len(data_list), smoothing=0)
        for chunk in chunker(data_list, num_threads):
            results = ray.get([c.generate_encoded_text.remote(row)
                               for c, row in list(zip(encoders, chunk))])

            # unnest and randomize results
            results = list(chain.from_iterable(results))
            shuffle(results)
            for result in results:
                w.write(result)

            pbar.update(num_threads)
        pbar.close()


@ray.remote(num_cpus=0.5)
class Encoder(object):
    def __init__(self, model, category_field,
                 keywords_field,
                 title_field,
                 body_field,
                 keyword_gen,
                 keyword_sep,
                 dropout,
                 repeat,
                 max_keywords,
                 keyword_length_max,
                 start_token,
                 end_token,
                 DELIMS,
                 PRONOUNS):
        self.nlp = spacy.load(model)
        self.pattern = re.compile('\W+')

        self.category_field = category_field
        self.keywords_field = keywords_field
        self.title_field = title_field
        self.body_field = body_field
        self.keyword_gen = keyword_gen
        self.keyword_sep = keyword_sep
        self.dropout = dropout
        self.repeat = repeat
        self.max_keywords = max_keywords
        self.keyword_length_max = keyword_length_max
        self.start_token = start_token
        self.end_token = end_token
        self.DELIMS = DELIMS
        self.PRONOUNS = PRONOUNS

    def build_section(self, section, text):
        if text is None:
            return ''
        return self.DELIMS['section'] + self.DELIMS[section] + text

    def generate_encoded_text(self, row):

        nlp = self.nlp
        pattern = self.pattern

        # category should be normalized to account for user input
        category = re.sub(
            pattern, '-', row[self.category_field].lower().strip()) if self.category_field is not None else None

        title = row[self.title_field] if self.title_field is not None else None
        body = row[self.body_field] if self.body_field is not None else None

        if self.keywords_field is None:
            # Generate the keywords using spacy
            doc = self.nlp(row[self.keyword_gen])
            keywords = [[chunk.text, chunk.root.text]
                        for chunk in doc.noun_chunks]
            keywords = [re.sub(self.pattern, '-', text.lower())
                        for text in chain.from_iterable(keywords)
                        if len(text) <= self.keyword_length_max]
        else:
            keywords = [re.sub(self.pattern, '-', keyword.lower().strip())
                        for keyword in row[self.keyword_gen].split(self.keyword_sep)]

        keywords = set(keywords) - self.PRONOUNS   # dedupe + remove pronouns

        encoded_texts = []
        for _ in range(self.repeat):
            new_keywords = [keyword for keyword in keywords
                            if random() < self.dropout]
            shuffle(new_keywords)
            new_keywords = " ".join(new_keywords[:self.max_keywords])

            encoded_texts.append(self.start_token +
                                 self.build_section('category', category) +
                                 self.build_section('keywords', new_keywords) +
                                 self.build_section('title', title) +
                                 self.build_section('body', body) +
                                 self.end_token + "\n")
        return encoded_texts
