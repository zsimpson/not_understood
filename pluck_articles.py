from plumbum import local
import json
import random

# PLUCK the control files randomly

input_folder = 'generated_data/extracted_articles'
output_path = 'generated_data/control_articles.jsoncr'
results_file = open(output_path, 'w')

article_count = 34175

output = open(output_path, 'w')

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
