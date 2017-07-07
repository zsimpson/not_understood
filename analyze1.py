'''
td-idf on a set of articles

Experiment #1: td-idf on the whole set of experiment articles vs the control articles.

Too much magic in gensim. I think I nee to do more of it myself so I understand/learn what's going on

'''
import json
import re
import sys
import math
from unidecode import unidecode
from collections import defaultdict
import nltk
import pickle
sno = nltk.stem.SnowballStemmer('english')

stem_cache = {}
def stem(word):
    global stem_cache
    stem = stem_cache.get(word)
    if stem is None:
        stem = sno.stem(word)
        stem_cache[word] = stem
    return stem


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
