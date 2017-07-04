from plumbum import local
import json
import random

input_folder = 'generated_data/extracted_articles'
output_path = 'generated_data/control_articles.jsoncr'
results_file = open(output_path, 'w')

article_count = 10

output = open(output_path, 'w')

# PLUCK the control files randomly
fps = [fp for fp in (local.cwd / input_folder).walk() if fp.is_file()]
for i in xrange(0,article_count):
    file_i = random.randint(0, len(fps))
    f = fps[file_i].open()
    lines = f.readlines()
    line_i = random.randint(0, len(lines))
    output.write(lines[line_i])
    f.close()

output.close()