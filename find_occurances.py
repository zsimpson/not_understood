from plumbum import local
import json
from unidecode import unidecode
import sys

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
            print occurance
            occurances += [occurance]
    return occurances


results_file = open('not_understood_occurances.jsoncr', 'w')

article_count = 0
occurance_count = 0

scan_count = 50000

for fp in (local.cwd / 'sample_data').walk():
    if article_count > scan_count:
        break
    f = fp.open()
    for line in f.readlines():
        if article_count > scan_count:
            break
        j = json.loads(line)
        occurances = scan_article(j['text'])
        results_file.write(
            json.dumps({
                'id': j['id'],
                'title': unidecode(j['title']),
                'z_occurances': occurances,
            }, sort_keys=True) + '\n'
        )
        article_count += 1
        occurance_count += len(occurances)
        results_file.flush()
    f.close()

results_file.close()

print '%d articles scanned', article_count
print '%d occurances', occurance_count