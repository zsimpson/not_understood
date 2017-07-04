from plumbum import local
import json
import random
import sys
import pandas as pd

# TODO combine the plucking files into one
# PLUCK the experiment lines

extracted_folder = 'generated_data/extracted_articles'
output_path = 'generated_data/experiment_articles.jsoncr'
occurances_path = 'generated_data/not_understood_occurances.jsoncr'
results_file = open(output_path, 'w')

file_lines = []
with (local.cwd / occurances_path).open() as f:
    for line in f:
        j = json.loads(line)
        file_lines += [(j['file'], j['line'])]

output = open(output_path, 'w')

file_lines.sort(key=lambda tup: tup[0])
df = pd.DataFrame(file_lines, columns=['filename', 'line_i'])

print 'Plucking'
# GROUP by file so we don't open the same file more than once
root_fp = local.path(extracted_folder)
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
