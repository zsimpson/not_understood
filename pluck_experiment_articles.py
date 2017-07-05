from plumbum import local
import json
import random
import sys
import pandas as pd

def pluck_lines_from_files(file_lines, output_path, root_path=''):
    '''
    file_lisnes is a list of tuples.
    Each tuple is (path, line).
    We wish to extract the specifed lines from the specified files.
    The file paths are optionallt prefixed with root_path.
    The files are written to output_path.
    This plucking is optimized by sorting and grouping by source file
    so that no source file is opened more than once.
    '''
    with open(output_path, 'w') as output:
        # CONVERT to dataframe for easy grouping
        file_lines.sort(key=lambda tup: tup[0])
        df = pd.DataFrame(file_lines, columns=['filename', 'line_i'])

        root_fp = local.path(root_path)
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


# PLUCK the experiment articles which is from the not_understood_occurances.jsoncr file
print 'Plucking experiment articles'
file_lines = []
with (local.cwd / 'generated_data/not_understood_occurances.jsoncr').open() as f:
    for line in f:
        j = json.loads(line)
        file_lines += [(j['file'], j['line'])]

pluck_lines_from_files(file_lines, 'generated_data/experiment_articles.jsoncr', 'generated_data/extracted_articles')


# PLUCK the control articles which are selected randomly
print 'Plucking control articles'
total_line_count = 0
all_file_lines = []
fps = [fp for fp in (local.cwd / 'generated_data/extracted_articles').walk() if fp.is_file()]
for i, fp in enumerate(fps):
    if i % 100 == 0:
        print i

    with fp.open() as f:
        line_count = sum((1 for i in f))
        file_name = '/'.join(fp.parts[-2:])
        total_line_count += line_count
        for j in xrange(0, line_count):
            all_file_lines += [(file_name, j)]

article_count = 100000
file_lines = []
for i in xrange(0, article_count):
    article_i = random.randint(0, total_line_count)
    file_lines += [all_file_lines[article_i]]

pluck_lines_from_files(file_lines, 'generated_data/control_articles.jsoncr', 'generated_data/extracted_articles')
