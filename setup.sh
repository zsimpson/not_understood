#!/usr/bin/env bash
pip install --user -r requirements.txt
mkdir -p primary_data
cd primary_data
wget https://dumps.wikimedia.org/enwiki/20170620/enwiki-20170620-pages-articles.xml.bz2
cd ..
mkdir -p external
cd external
git clone https://github.com/attardi/wikiextractor.git
cd ..

