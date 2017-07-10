'''
td-idf on a set of articles

Experiment #1: td-idf on the whole set of experiment articles vs the control articles.

Too much magic in gensim. I think I nee to do more of it myself so I understand/learn what's going on

'''
import json
import re
from unidecode import unidecode
import pickle
import nltk
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pylab
matplotlib.style.use('ggplot')
from collections import Counter
sno = nltk.stem.SnowballStemmer('english')


stem_cache = {}
def stem(word):
    global stem_cache
    stem = stem_cache.get(word)
    if stem is None:
        stem = sno.stem(word)
        stem_cache[word] = stem
    return stem


class BOW(Counter):
    @classmethod
    def from_text(cls, text):
        bow = cls()
        text = unidecode(text.lower())
        # for word in re.split("[^a-z']+", text):
        #     bow[stem(word)] += 1
        bow.update(re.split("[^a-z']+", text))
        del bow['']
        return bow

    def to_df(self):
        return pd.DataFrame(self.items(), columns=['word', 'word_count'])


def jsoncr_iter(filename, fields, subsample_count):
    i = 0
    for line in open(filename):
        if i % 10 == 0:
            print i
        i += 1
        if i <= subsample_count:
            j = json.loads(line)
            yield tuple([j[f] for f in fields])
        else:
            break


counts_filename = 'generated_data/bow_counts_unstemmed_phrase1.pickle'
regen = True
if regen:
    subsample_doc_count = 9e9
    corpus_titles = []
    corpus_bow = BOW()
    corpus_doc_count = BOW()
    for title, text in jsoncr_iter('generated_data/control_articles.jsoncr', ['title', 'text'], subsample_doc_count):
        bow = BOW.from_text(text)
        total = sum(bow.values())
        if total > 100:
            corpus_titles += [title]
            corpus_bow.update(bow)
            for word in bow.keys():
                corpus_doc_count[word] += 1

    experiment_titles = []
    experiment_bow = BOW()
    for title, text in jsoncr_iter('generated_data/experiment_articles.jsoncr', ['title', 'text'], subsample_doc_count):
        if u'not well understood' in text:
            experiment_titles += [title]
            bow = BOW.from_text(text)
            experiment_bow.update(bow)

    with open(counts_filename, 'w') as f:
        pickle.dump(
            {
                'corpus_titles': corpus_titles,
                'corpus_bow': corpus_bow,
                'corpus_doc_count': corpus_doc_count,
                'experiment_titles': experiment_titles,
                'experiment_bow': experiment_bow,
            }, f
        )
else:
    with open(counts_filename) as f:
        loaded = pickle.load(f)
        corpus_titles = loaded['corpus_titles']
        corpus_bow = loaded['corpus_bow']
        corpus_doc_count = loaded['corpus_doc_count']
        experiment_titles = loaded['experiment_titles']
        experiment_bow = loaded['experiment_bow']


corpus_df = corpus_bow.to_df()
corpus_df.sort_values(by='word_count', ascending=False, inplace=True)
corpus_df.drop(corpus_df.index[:500], inplace=True)

corpus_doc_count_df = corpus_doc_count.to_df()
corpus_doc_count_df = corpus_doc_count_df[corpus_doc_count_df.word_count > 1]

experiment_df = experiment_bow.to_df()
doc_count = len(corpus_titles)

merged = pd.merge(corpus_df, corpus_doc_count_df, on='word', how='inner', suffixes=['_tf', '_df'])
merged['idf'] = np.log(doc_count / (1 + merged.word_count_df))

# Sanity check that the tdidf of the control is mostly small
merged['tfidf'] = merged.word_count_tf * merged.idf
merged.sort_values(by='tfidf', ascending=False, inplace=True)
print merged[0:30]
# hist = merged.tfidf[0:500]
# pos = pylab.arange(500)+.5
# plt.barh(pos, hist)
# plt.savefig('control.png')
# plt.show()

baseline = merged.tfidf.iloc[0] * 1.3
print 'baseline', baseline
tfidf = pd.merge(merged, experiment_df, on='word', how='inner')
tfidf.rename(columns={'word_count': 'experiment_tf'}, inplace=True)
tfidf['tfidf'] = tfidf.experiment_tf * tfidf.idf
tfidf.sort_values(by='tfidf', ascending=False, inplace=True)
for i, row in tfidf[tfidf.tfidf > baseline].iterrows():
    print row.word, row.tfidf

# print tfidf[0:30]
# hist = tfidf.tfidf[0:500]
# pos = pylab.arange(500)+.5
# plt.barh(pos, hist)
# plt.savefig('experiment.png')
# plt.show()

'''
corpus_total_words = corpus_df.word_count.sum()
corpus_df['freq'] = corpus_df.word_count / corpus_total_words

experiment_total_words = experiment_df.word_count.sum()
experiment_df['freq'] = experiment_df.word_count / experiment_total_words

compare_df = pd.merge(corpus_df, experiment_df, on='word', how='left', suffixes=['_corpus', '_experiment'])
compare_df.fillna(0, inplace=True)

compare_df['score'] = compare_df.freq_experiment / compare_df.freq_corpus
compare_df.sort_values(by='score', ascending=False, inplace=True)
compare_df.to_pickle('generated_data/analysis2.pickle')
print compare_df[0:100]
'''

'''

corpus_df = corpus_bow.to_df()
corpus_total_words = corpus_df.word_count.sum()
corpus_df['freq'] = corpus_df.word_count / corpus_total_words

experiment_df = experiment_bow.to_df()
experiment_total_words = experiment_df.word_count.sum()
experiment_df['freq'] = experiment_df.word_count / experiment_total_words

compare_df = pd.merge(corpus_df, experiment_df, on='word', how='left', suffixes=['_corpus', '_experiment'])
compare_df.fillna(0, inplace=True)

compare_df['score'] = compare_df.freq_experiment / compare_df.freq_corpus
compare_df.sort_values(by='score', ascending=False, inplace=True)
compare_df.to_pickle('generated_data/analysis2.pickle')
print compare_df[0:100]
'''

'''
c = 0
for line in open('generated_data/experiment_articles.jsoncr'):
    c += 1
    if c > stop_at:
        break

    j = json.loads(line)
    self.experiment_docs += [j['title']]
    yield (j['title'], j['text'])


class WordBag(dict):
    def __init__(self, text=None):
        if text is not None:
            self.accumulate_text(text)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            self[key] = 0
            return 0

    def __mul__(self, other):
        result = WordBag()
        for word, value in self.iteritems():
            result[word] = other.get(word, 0.0) * self.get(word, 0.0)
        return result

    def __div__(self, scalar):
        result = WordBag()
        for word, value in self.iteritems():
            result[word] = self[word] / scalar
        return result

    def accumulate_text(self, text):
        text = unidecode(text.lower())
        for word in re.split("[^a-z']+", text):
            self[stem(word)] += 1

    def by_rank(self):
        return sorted(self.items(), key=lambda x: x[1], reverse=True)

    def merge(self, other):
        for word, count in other.iteritems():
            self[word] += count


class TfIdfAnalyzer(object):
    def __init__(self):
        self.doc_names = []
        self.doc_count_by_word = WordBag()
        self.idf = WordBag()
        self.tf_by_doc = {}

    def analyze_docs(self, docs_generator):
        doc_count = 0
        for doc_name, doc_text in docs_generator:
            if doc_count % 10 == 0:
                print doc_count
            tf = WordBag(doc_text)
            total_words = sum(tf.values())
            if total_words > 100:
                doc_count += 1
                self.doc_names += [doc_name]
                for word, count in tf.iteritems():
                    self.doc_count_by_word[word] += 1
                self.tf_by_doc[doc_name] = tf / float(total_words)
            else:
                self.tf_by_doc[doc_name] = WordBag()

        # COMPUTE the idf
        for word, count in self.doc_count_by_word.iteritems():
            self.idf[word] = math.log(float(doc_count) / (1.0 + float(count)))

    def tfidf_by_doc(self, doc_name):
        # COMPUTE the tf-idf for each document
        return self.tf_by_doc[doc_name] * self.idf

    def save(self, filename):
        with open(filename, 'w') as f:
            pickle.dump(self.__dict__, f)

    def load(self, filename):
        with open(filename) as f:
            self.__dict__.update(pickle.load(f))


class AllDocIter(object):
    def __init__(self):
        self.control_docs = []
        self.experiment_docs = []

    def __iter__(self):
        stop_at = 9e9
        c = 0
        for line in open('generated_data/control_articles.jsoncr'):
            c += 1
            if c > stop_at:
                break

            j = json.loads(line)
            self.control_docs += [j['title']]
            yield (j['title'], j['text'])

        c = 0
        for line in open('generated_data/experiment_articles.jsoncr'):
            c += 1
            if c > stop_at:
                break

            j = json.loads(line)
            self.experiment_docs += [j['title']]
            yield (j['title'], j['text'])


tfidf_analyzer = TfIdfAnalyzer()
all_doc_iter = AllDocIter()

tfidf_filename = 'generated_data/tfidf.pickle'
exp_doc_names_filename = 'generated_data/experiment_doc_names.pickle'

rerun = True
if rerun:
    tfidf_analyzer.analyze_docs(all_doc_iter)
    tfidf_analyzer.save(tfidf_filename)
    with open(exp_doc_names_filename, 'w') as f:
        pickle.dump(all_doc_iter.experiment_docs, f)
else:
    tfidf_analyzer.load(tfidf_filename)
    with open(exp_doc_names_filename) as f:
        all_doc_iter.experiment_docs = pickle.load(f)


# Treat the whole experiment group as one big document
# to see what words come out high in that as a group

# MERGE all of the term frequencies for the experiment group into one
experiment_wb = WordBag()
for doc_name in all_doc_iter.experiment_docs:
    experiment_wb.merge(tfidf_analyzer.tf_by_doc[doc_name])

# COMPUTE 
tfidf_for_experiment = experiment_wb * tfidf_analyzer.idf

for word, score in tfidf_for_experiment.by_rank()[0:100]:
    print word, score
'''