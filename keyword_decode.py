import re

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

    # get the index of the group(s) we want to extract
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


def keyword_decode_file(file_path, out_file='texts_decoded.txt',
                        doc_delim='=' * 20 + '\n',
                        input_sections=['keywords', 'titles'],
                        output_sections=['titles'],
                        start_token="<|startoftext|>",
                        end_token="<|endoftext|>"):

    section_pattern = build_pattern(input_sections)
    doc_pattern = re.compile(
        re.escape(start_token + '(.*)' + end_token), flags=re.MULTILINE)

    with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
        # warning: loads entire file into memory!
        docs = re.match(doc_pattern(f.read()))

    decoded_docs = keyword_decode(docs, pattern=section_pattern,
                                  input_sections=input_sections,
                                  output_sections=output_sections)

    with open(out_file, 'r', encoding='utf8', errors='ignore') as f:
        for doc in decoded_docs:
            f.write("{}\n{}".format(doc, doc_delim))
