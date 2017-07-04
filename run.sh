#!/usr/bin/env bash

# Run time, about 3 hours with 4 cpus
echo "Start time"
date
python ./external/wikiextractor/WikiExtractor.py \
    --processes 4 \
    --output ./generated_data/extracted_articles \
    --bytes 10M \
    --json \
    --filter_disambig_pages \
    --no-templates \
    ./primary_data/enwiki-20170620-pages-articles.xml
echo "End time"
date

