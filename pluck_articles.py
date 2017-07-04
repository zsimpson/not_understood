from plumbum import local
import json
import random
import sys

# PLUCK the control files randomly

input_folder = 'generated_data/extracted_articles'
output_path = 'generated_data/control_articles.jsoncr'
results_file = open(output_path, 'w')


fps = [fp for fp in (local.cwd / input_folder).walk() if fp.is_file()]
for i, fp in enumerate(fps):
    print i, sum((1 for i in open(file_path, 'rb')))

sys.exit()

article_count = 34175

output = open(output_path, 'w')

files_and_lines = []

fps = [fp for fp in (local.cwd / input_folder).walk() if fp.is_file()]
for i in xrange(0,article_count):
    if i % 100 == 0:
        print i
    file_i = random.randint(0, len(fps))
    f = fps[file_i].open()
    lines = f.readlines()
    line_i = random.randint(0, len(lines))
    output.write(lines[line_i])
    f.close()

output.close()
