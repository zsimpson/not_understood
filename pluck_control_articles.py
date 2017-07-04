from plumbum import local
import json
import random
import sys
import pandas as pd

# PLUCK the control files randomly

input_folder = 'generated_data/extracted_articles'
output_path = 'generated_data/control_articles.jsoncr'
results_file = open(output_path, 'w')

# ACCUMULATE a list of line counts in each file
print 'Counting lines'
total_line_count = 0
file_lines = []
fps = [fp for fp in (local.cwd / input_folder).walk() if fp.is_file()]
for i, fp in enumerate(fps):
    if i % 100 == 0:
        print i
    f = fp.open()
    line_count = sum((1 for i in f))
    file_name = '/'.join(fp.parts[-2:])
    total_line_count += line_count
    for j in xrange(0, line_count):
        file_lines += [(file_name, j)]
    f.close()

article_count = 100000

output = open(output_path, 'w')

print 'Sampling'
samples = []
for i in xrange(0, article_count):
    article_i = random.randint(0, total_line_count)
    samples += [file_lines[article_i]]

samples.sort(key=lambda tup: tup[0])
df = pd.DataFrame(samples, columns=['filename', 'line_i'])

print 'Plucking'
# GROUP by file so we don't open the same file more than once
root_fp = local.path(input_folder)
grouped = df.groupby('filename')
for filename, group in grouped:
    with (root_fp / filename).open() as f:
        line_indicies = sorted(list(group.line_i))
        last_line_index = line_indicies[-1]
        for i, line in enumerate(f):
            if i in line_indicies:
                output.write(line)
            if i == last_line_index:
                break

output.close()
