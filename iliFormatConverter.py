# Author: Ivan Protsyuk <ivan.protsyuk@embl.de>.

# KNIME environment:
#     input_table_1 - a DataFrame with a single cell containing a path to a file produced by FeatureLinkerUnlabeledQT
#     input_table_2 - a DataFrame containing names and spatial coordinates of LC-MS samples.
#     flow_variables - a dictionary with KNIME flow variables.

__version__ = '0.1'

from pandas import DataFrame
from pandas import Series

import csv
import os

def datafilter(iterator):
    """Generator skipping empty lines and lines starting with the comment_start"""
    for line in iterator:
        if line.strip() and not line.startswith('#'):
            yield line


input_file_path = input_table_1['URI'][0]
uri_prefix = flow_variables['URI_FILE_PREFIX']
if input_file_path.startswith(uri_prefix):
    input_file_path = input_file_path[len(uri_prefix):]

output_table = input_table_2

with open(input_file_path) as input_file:
    file_names = {}
    sample_names = output_table[output_table.columns.values[0]].tolist()
    last_column_number = len(output_table.columns) - 1
    reader = csv.reader(datafilter(input_file))
    for row in reader:
        if row[0] == 'MAP':
            file_names[int(row[1])] = os.path.splitext(os.path.basename(row[2]))[0]
        elif row[0] == 'CONSENSUS':
            output_table[row[2]] = Series([0] * len(output_table))
            last_column_number += 1
            for map_number in file_names:
                intensity = row[9 + map_number * 5]
                intensity = int(intensity) if intensity != 'nan' else 0
                if not file_names[map_number] in sample_names:
                    raise ValueError('File name "%s" is not found in the first column of the file with spatial coordinates of samples.' % file_names[map_number])
                row_number = sample_names.index(file_names[map_number])
                output_table.iloc[row_number, last_column_number] = intensity
