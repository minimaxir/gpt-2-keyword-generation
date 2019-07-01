import re

DELIMS = {
    'section': '~',
    'category': '`',
    'keywords': '^',
    'title': '@',
    'body': '}'
}


def build_pattern(sections, start_token, end_token):
    pattern_text = re.escape(start_token) + '(?:.*)'

    for section in sections:
        pattern_text += '(?:{})'.format(
            re.escape(DELIMS['section'] + DELIMS[section])) + '(.*)'

    pattern_text += '(?:.*)' + re.escape(end_token)

    return re.compile(pattern_text, flags=re.MULTILINE)


def keyword_decode(texts, input_sections=['keywords', 'title'],
                   output_sections=['title'],
                   start_token="<|startoftext|>",
                   end_token="<|endoftext|>"):

    # get the index of the group(s) we want to extract
    group_indices = [i + 1 for i, section in enumerate(input_sections)
                     if section in output_sections]

    assert len(group_indices) > 0
    pattern = build_pattern(input_sections, start_token, end_token)
    decoded_texts = []
    for text in texts:
        decoded_text = re.match(pattern, text)
        if decoded_text is None:
            continue
        decoded_text_attrs = (decoded_text.group(i) for i in group_indices)
        decoded_texts.append(decoded_text_attrs)
    return decoded_texts


def keyword_decode_file(file_path, out_file='texts_decoded.txt',
                        doc_delim='=' * 20 + '\n',
                        input_sections=['keywords', 'titles'],
                        output_sections=['titles'],
                        start_token="<|startoftext|>",
                        end_token="<|endoftext|>"):

    doc_pattern = re.compile(
        re.escape(start_token + '(.*)' + end_token), flags=re.MULTILINE)

    with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
        # warning: loads entire file into memory!
        docs = re.match(doc_pattern(f.read()))

    decoded_docs = keyword_decode(docs, input_sections=input_sections,
                                  output_sections=output_sections,
                                  start_token=start_token,
                                  end_token=end_token)

    with open(out_file, 'w', encoding='utf8', errors='ignore') as f:
        for doc in decoded_docs:
            f.write("{}\n{}".format(doc, doc_delim))
