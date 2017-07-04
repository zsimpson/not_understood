from plumbum import local
import json
from unidecode import unidecode
import sys

input_folder = 'generated_data/extracted_articles'
output_path = 'generated_data/not_understood_occurances.jsoncr'
results_file = open(output_path, 'w')


def findall(sub, string):
    index = 0 - len(sub)
    try:
        while True:
            index = string.index(sub, index + len(sub))
            yield index
    except ValueError:
        pass


phrases = [
    'is not well understood',
    'is not understood well',
    'are not well understood',
    'are not understood well',
    'remain mysterious',
    'remains mysterious',
    'is unknown',
    'are unknown',
    'is obscure',
    'are obscure'
]


def scan_article(text):
    text = text.replace('\n', ' ')
    text = text.replace('  ', ' ')
    text = text.lower()
    context_len = 200
    len_text = len(text)-1
    occurances = []
    for phrase in phrases:
        for i in findall(phrase, text):
            try:
                head_i = max(0, i-context_len)
                tail_i = min(len_text, i+len(phrase)+context_len)

                # Keep only words... cut based on near whitespace (always shortening the strings)
                head = text[head_i:i]
                head = head.split(' ', 1)[1]
                tail = text[i+len(phrase):tail_i]
                tail = tail.rsplit(' ', 1)[0]
                middle = text[i:i+len(phrase)]

                occurance = (
                    unidecode(head),
                    unidecode(middle),
                    unidecode(tail)
                )
                occurances += [occurance]
            except:
                pass
    return occurances


article_count = 0
occurance_count = 0

for fp in (local.cwd / input_folder).walk():
    if not fp.is_file():
        continue

    f = fp.open()
    for line_i, line in enumerate(f.readlines()):
        if article_count % 10000 == 0:
            print article_count

        j = json.loads(line)
        occurances = scan_article(j['text'])
        article_count += 1
        if len(occurances) > 0:
            results_file.write(
                json.dumps({
                    'id': j['id'],
                    'title': unidecode(j['title']),
                    'file': '/'.join(fp.parts[-2:]),
                    'line': line_i,
                    'text_len': len(j['text']),
                    'z_occurances': occurances,
                }, sort_keys=True) + '\n'
            )
            occurance_count += len(occurances)
            results_file.flush()
    f.close()

results_file.close()

print '%d articles scanned', article_count
print '%d occurances', occurance_count
