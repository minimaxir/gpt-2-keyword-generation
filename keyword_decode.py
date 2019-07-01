import re

DELIMS = {
    'section': '~',
    'category': '`',
    'keywords': '^',
    'title': '@',
    'body': '}'
}


def build_pattern(sections, start_token, end_token):
    # sections may not be in the correct order: fix it
    key_order = ['category', 'keywords', 'title', 'body']
    sections = [section for section in key_order if section in sections]

    pattern_text = re.escape(start_token) + '(?:.*)'

    for section in sections:
        pattern_text += '(?:{})'.format(
            re.escape(DELIMS['section'] + DELIMS[section])) + '(.*)'

    pattern_text += '(?:.*)' + re.escape(end_token)

    return re.compile(pattern_text, flags=re.MULTILINE)


def decode_texts(texts, sections=['title'],
                 start_token="<|startoftext|>",
                 end_token="<|endoftext|>"):

    # get the index of the group(s) we want to extract
    group_indices = [i + 1 for i, section in enumerate(sections)]

    assert len(group_indices) > 0
    pattern = build_pattern(sections, start_token, end_token)
    if not isinstance(texts, (list,)):
        texts = [texts]
    decoded_texts = []
    for text in texts:
        decoded_text = re.match(pattern, text)
        if decoded_text is None:
            continue
        decoded_text_attrs = tuple(decoded_text.group(i)
                                   for i in group_indices)
        if len(group_indices) == 1:
            decoded_text_attrs = decoded_text_attrs[0]
        decoded_texts.append(decoded_text_attrs)
    return decoded_texts


def decode_file(file_path, out_file='texts_decoded.txt',
                doc_delim='=' * 20 + '\n',
                sections=['title'],
                start_token="<|startoftext|>",
                end_token="<|endoftext|>"):

    assert len(sections) == 1, "This function only supports output of a single section for now."
    doc_pattern = re.compile(re.escape(start_token) +
                             '(.*)' + re.escape(end_token), flags=re.MULTILINE)

    with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
        # warning: loads entire file into memory!
        docs = re.findall(doc_pattern, f.read())

    docs = [start_token + doc + end_token for doc in docs]
    decoded_docs = decode_texts(docs,
                                sections=sections,
                                start_token=start_token,
                                end_token=end_token)

    with open(out_file, 'w', encoding='utf8', errors='ignore') as f:
        for doc in decoded_docs:
            f.write("{}\n{}".format(doc, doc_delim))
