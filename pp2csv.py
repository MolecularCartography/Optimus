import csv
import os
import sys
import xml.etree.ElementTree as etree


FILE_NAME_HEADER = 'Sample name'
X_COORD_HEADER = 'x'
Y_COORD_HEADER = 'y'
Z_COORD_HEADER = 'z'
RADIUS_COORD_HEADER = 'r'

output_file_path = 'coords.csv'


def pp2csv(source_file, point_radius):
    result_table = []
    # headers
    result_table.append([FILE_NAME_HEADER])
    result_table.append([X_COORD_HEADER])
    result_table.append([Y_COORD_HEADER])
    result_table.append([Z_COORD_HEADER])

    tree = etree.parse(source_file)
    root = tree.getroot()
    for node in root.findall('./point'):
        if node.get('active') == '1':
            result_table[0].append(node.get('name'))
            result_table[1].append(node.get('x'))
            result_table[2].append(node.get('y'))
            result_table[3].append(node.get('z'))
    result_table.append([RADIUS_COORD_HEADER] + [point_radius] * (len(result_table[0]) - 1))
    return result_table


if len(sys.argv) != 3:
    raise ValueError('''This script expects two arguments:\n
    1. path to a file, created with MeshLab, with coordinates of sampling points;\n
    2. radius of sampling points.''')
elif not os.path.exists(sys.argv[1]):
    raise ValueError('File "%s" is not found.' % sys.argv[1])
elif float(sys.argv[2]) <= 0:
    raise ValueError('Sampling point radius is expected to be a positive number.' % sys.argv[2])

table = pp2csv(sys.argv[1], sys.argv[2])

with open(output_file_path, 'wb') as output_file:
    writer = csv.writer(output_file)
    for idx, sample_name in enumerate(table[0]):
        writer.writerow([sample_name, table[1][idx], table[2][idx], table[3][idx], table[4][idx]])
