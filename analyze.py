'''
td-idf on a set of articles

Experiment #1: td-idf on the whole set of experiment articles vs the control articles.

Too much magic in gensim. I think I nee to do more of it myself so I understand/learn what's going on

'''
import json
import re
import sys
from unidecode import unidecode
from gensim import corpora, models, similarities

# dictionary = corpora.Dictionary()
dictionary = corpora.Dictionary()

class MyCorpus(object):
    def __iter__(self):
        for line in open('generated_data/control_articles.jsoncr'):
            text = json.loads(line)['text'].lower()
            yield dictionary.doc2bow(re.split('\W+', text), allow_update=True)

corpus = MyCorpus()


# for i, vector in enumerate(corpus):
#     if i % 100 == 0:
#         print i
# dictionary.save('generated_data/control.dict')

dictionary.load('generated_data/control.dict')

tfidf = models.TfidfModel(corpus)

