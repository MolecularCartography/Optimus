# Author: Ivan Protsyuk <ivan.protsyuk@embl.de>.

""" This module is a command line program that serves for automatic tuning of a feature detection algorithm
FeatureFinderMetabo distributed as a part of the OpenMS toolbox (www.openms.de).
"""

__version__ = '0.1'

from lxml import etree

import argparse
import csv
import datetime
import multiprocessing
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

OPTIMAL_THREAD_COUNT = multiprocessing.cpu_count()
INFO_OUTPUT_PREFIX = 'INFO: '
CSV_COMMENT_START = '#'
EXPECTED_FEATURES_FILE_EXT = '.csv'
WORKFLOW_RESULT_FILE_EXT = '.csv'
OUTPUT_FILE_NAME = 'output.csv'
DEFAULT_RT = -1

def loginfo(message):
    print('[%s] %s%s' % (datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), INFO_OUTPUT_PREFIX, message))

def getstandardfilenames(path):
    """Returns a dictionary where keys are paths to files that contain expected features and values are corresponding files with LC-MS data.
    """
    loginfo('Locating files with LC-MS data...')

    input_file_paths = os.listdir(path)
    sample_by_expected_features = {}
    for expected_features_file in input_file_paths:
        if expected_features_file.endswith(EXPECTED_FEATURES_FILE_EXT):
            is_associated_file_found = False
            expected_features_file_wo_ext = os.path.splitext(os.path.basename(expected_features_file))[0]
            for associated_file in input_file_paths:
                if associated_file != expected_features_file and os.path.splitext(os.path.basename(associated_file))[0] == expected_features_file_wo_ext:
                    is_associated_file_found = True
                    sample_by_expected_features[os.path.join(path, expected_features_file)] = os.path.join(path, associated_file)
                    break

            if not is_associated_file_found:
                loginfo('File with LC-MS data associated with "%s" is not found.' % os.path.abspath(expected_features_file))

    if not sample_by_expected_features:
        raise ValueError('The directory with workflow input data does not contain CSV-files with expected features.')

    loginfo('%d files have been found in the input directory.\n' % len(sample_by_expected_features))

    return sample_by_expected_features


def commentstripper(iterator):
    """Generator skipping empty lines and lines starting with the comment_start.
    """
    for line in iterator:
        if line.strip() and not line.startswith(CSV_COMMENT_START):
            yield line


def isnumber(s):
    """Checks if s can be converted to Float.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def getexpectedfeaturesfromfile(file):
    """Returns list of features from csv file.
    
    The input file is filtered using commentstripper. Only first two columns of the file are considered. The 1st one corresponds to mz values, the 2nd one is for RT values.
    The result object is a dictionary where mz is a key, and RT is a value.
    """
    loginfo('Reading expected features from "%s"...' % file)

    result = {}
    with open(file) as file_with_standards:
        reader = csv.reader(commentstripper(file_with_standards))
        for row in reader:
            if len(row) < 1:
                raise ValueError('Empty row is found unexpectedly in "%s"' % file)
            else:
                current_mass = float(row[0])
                if current_mass in result:
                    loginfo('Mass value of %.5f is duplicated.' % current_mass)
                elif len(row) == 1 or not isnumber(row[1]):
                    result[current_mass] = DEFAULT_RT
                else:
                    result[current_mass] = float(row[1]) # {mz : rt}

    loginfo('%d features have been read.\n' % len(result))
    return result


def setnoiseleveltoworkflow(root, noise_level):
    """Assigns the noise_threshold_int parameter from XML file provided by root to noise_level.
    """
    noise_threshold_nodes = root.findall('./NODE/NODE/ITEM[@name="tool_name"][@value="FeatureFinderMetabo"]'
                                         '/../NODE[@name="parameters"]/NODE[@name="algorithm"]/NODE[@name="common"]/ITEM[@name="noise_threshold_int"]')
    if len(noise_threshold_nodes) != 1:
        raise ValueError('Workflow file is invalid. The FeatureFinderMetabo node does not have the "noise_threshold_int" parameter.')

    noise_threshold_nodes[0].set('value', str(noise_level))


def setinputfilestoworkflow(root, raw_standard_file_paths):
    """Asigns standard_file_paths to the workflow input.
    """
    input_files_list = root.findall('./NODE/NODE/ITEM[@name="toppas_type"][@value="input file list"]/../ITEMLIST[@name="file_names"]')
    if len(input_files_list) != 1:
        raise ValueError('Workflow file is invalid. The "Input files" node does not have the "file_names" parameter.')

    for input_file in input_files_list[0]:
        input_files_list[0].remove(input_file)

    for raw_standard_file in raw_standard_file_paths:
        etree.SubElement(input_files_list[0], 'LISTITEM', {'value' : os.path.abspath(raw_standard_file)});


def setworkflowthreadnumber(root, thread_number):
    """Assigns the threads parameter of workflow nodes to thread_number.
    """
    for node in root.findall('./NODE/NODE/NODE[@name="parameters"]/ITEM[@name="threads"]'):
        node.set('value', str(thread_number))


def setfeaturedetectionmasserror(root, mass_error_ppm):
    """Assigns the mass_error_ppm parameter of the FindFeatureMetabo workflow node to mass_error_ppm.
    """
    mass_error_nodes = root.findall('./NODE/NODE/ITEM[@name="tool_name"][@value="FeatureFinderMetabo"]'
                                    '/../NODE[@name="parameters"]/NODE[@name="algorithm"]/NODE[@name="mtd"]/ITEM[@name="mass_error_ppm"]')
    if len(mass_error_nodes) != 1:
        raise ValueError('Workflow file is invalid. The FeatureFinderMetabo node does not have the "mass_error_ppm" parameter.')

    mass_error_nodes[0].set('value', str(mass_error_ppm))


def runworkflow(openms_base_dir_path, path_to_workflow, path_to_results, noise_level):
    """Runs the TOPPAS workflow with noise_level and stores results to path_to_results
    """
    tree = etree.parse(path_to_workflow)
    root = tree.getroot()

    setnoiseleveltoworkflow(root, noise_level)
    tree.write(path_to_workflow)

    null_out_stream = open(os.devnull, 'w')
    # TODO: Check if standard path to the ExecutePipeline executable file depends on a current OS
    command = '%s -in "%s" -out_dir "%s" -num_jobs %d' % (os.path.join(openms_base_dir_path, 'bin', 'ExecutePipeline'), path_to_workflow, path_to_results, OPTIMAL_THREAD_COUNT)
    loginfo('Calling feature detection with the noise level %.2E ...' % noise_level)
    subprocess.call(command, stdout = null_out_stream, stderr = null_out_stream, shell = False)


def calculateproportionofexpectedfeatures(path_to_calculated_features, expected_features, mzt):
    """Returns the proportion of expected features spotted by the workflow relatively to overall number of expected features.
    
    Counts the number of expected features matched features produced by the workflow taking mzt into account.
    Returns this number divided by the total number of expected features.
    """
    count_of_expected_features = 0
    for standard in expected_features.values():
        count_of_expected_features += len(standard)

    count_of_matched_features = 0
    total_number_of_features = 0
    for file_name in expected_features:
        calculated_features = {}
        workflow_result_file_name = os.path.splitext(os.path.basename(file_name))[0] + WORKFLOW_RESULT_FILE_EXT # workflow output files have same base names as the input ones
        with open(os.path.join(path_to_calculated_features, workflow_result_file_name)) as file_with_standards:
            reader = csv.reader(commentstripper(file_with_standards))
            for row in reader:
                calculated_features[float(row[2])] = [float(row[9]), float(row[10])] # {mz : [rt_min, rt_max]}

        total_number_of_features += len(calculated_features)
        for expected_mz in expected_features[file_name].keys():
            for calculated_mz in calculated_features:
                ppm = expected_mz / 1000000
                expected_rt = expected_features[file_name][expected_mz]
                min_calculated_rt = calculated_features[calculated_mz][0]
                max_calculated_rt = calculated_features[calculated_mz][1]

                mz_matched = expected_mz - mzt * ppm <= calculated_mz and calculated_mz <= expected_mz + mzt * ppm
                rt_matched = expected_rt == DEFAULT_RT or min_calculated_rt <= expected_rt and expected_rt <= max_calculated_rt

                if mz_matched and rt_matched:
                    count_of_matched_features += 1
                    break

    loginfo('Total number of detected features is %d.' % total_number_of_features)
    loginfo('%d out of %d expected features have been detected (%.2f%%).\n' % (count_of_matched_features, count_of_expected_features, 100 * float(count_of_matched_features) / count_of_expected_features))
    return float(count_of_matched_features) / count_of_expected_features

def getpathtoworkflowresults(path_to_workflow_output):
    """Returns a path to a directory containing files produced by the TOPPAS workflow.

    The current implementation assumes that it's the second nested directory to path_to_workflow_output.
    """
    for root1, dirs1, files1 in os.walk(path_to_workflow_output):
        first_subdir = os.path.join(path_to_workflow_output, dirs1[0])
        if os.path.isdir(first_subdir):
            for root2, dirs2, files2 in os.walk(first_subdir):
                second_subdir = os.path.join(first_subdir, dirs2[0])
                if os.path.isdir(second_subdir):
                    return second_subdir

    raise RuntimeError('TOPPAS workflow results not found.')


def reporttuningresults(noise_level, proportion_of_detected_features):
    """Shows an info message that workflow tuning ended up with provided values of noise_level and proportion_of_detected_features.
    """
    loginfo('Workflow tuning has been finished successfully.\n\tNoise level: %.2E.\n\tPercentage of detected expected features: %.2f.\n' % (noise_level, 100 * proportion_of_detected_features))


def tuneworkflow(workflow_settings, expected_features):
    """Modifies a file with TOPPAS workflow located in path_to_workflow so that it detects required proportion of expected features.
    """
    tree = etree.parse(workflow_settings.workflow_file_path)
    root = tree.getroot()

    setinputfilestoworkflow(root, expected_features.keys())
    setworkflowthreadnumber(root, OPTIMAL_THREAD_COUNT)
    setfeaturedetectionmasserror(root, workflow_settings.mz_tolerance_ppm)
    tree.write(workflow_settings.workflow_file_path)

    high_noise_level = workflow_settings.max_noise_level
    low_noise_level = workflow_settings.min_noise_level
    current_proportion_of_detected_features = 0
    min_proportion = workflow_settings.required_expected_features_proportion - workflow_settings.features_proportion_precision
    max_proportion = workflow_settings.required_expected_features_proportion + workflow_settings.features_proportion_precision

    # fast check: if there is enough features with the highest noise level then the tuning is over
    runworkflow(workflow_settings.openms_base_dir_path, workflow_settings.workflow_file_path, workflow_settings.workflow_output_dir, high_noise_level)
    path_to_workflow_results = getpathtoworkflowresults(workflow_settings.workflow_output_dir)
    current_proportion_of_detected_features = calculateproportionofexpectedfeatures(path_to_workflow_results, expected_features, workflow_settings.mz_tolerance_ppm)
    if current_proportion_of_detected_features >= min_proportion:
        reporttuningresults(high_noise_level, current_proportion_of_detected_features)
        return high_noise_level

    while (current_proportion_of_detected_features < min_proportion or max_proportion < current_proportion_of_detected_features) and high_noise_level - low_noise_level > 1:
        current_noise_level = (high_noise_level + low_noise_level) / 2
        runworkflow(workflow_settings.openms_base_dir_path, workflow_settings.workflow_file_path, workflow_settings.workflow_output_dir, current_noise_level)

        current_proportion_of_detected_features = calculateproportionofexpectedfeatures(path_to_workflow_results, expected_features, workflow_settings.mz_tolerance_ppm)

        if current_proportion_of_detected_features < min_proportion:
            high_noise_level = current_noise_level
        elif max_proportion < current_proportion_of_detected_features:
            low_noise_level = current_noise_level
        else:
            reporttuningresults(current_noise_level, current_proportion_of_detected_features)
            return current_noise_level


def getworkflowoutputdirpath():
    """Creates a directory for storing workflow results and returns a path to it.
    """
    output_dir = os.path.abspath('./output_data')
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    return output_dir


def directorypath(arg):
    """Checks if path actually points to a directory and that directory exists.
    """
    path = str(arg)
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError('%r is not a directory.' % path)
    elif not os.path.exists(path):
        raise argparse.ArgumentTypeError('%r does not exist.' % path)
    else:
        return os.path.abspath(path)


def filepath(arg):
    """Checks if path actually points to a file and that file exists.
    """
    path = str(arg)
    if os.path.isdir(path):
        raise argparse.ArgumentTypeError('%r is a directory.' % path)
    elif not os.path.exists(path):
        raise argparse.ArgumentTypeError('%r does not exist.' % path)
    else:
        return os.path.abspath(path)

def nonnegativeinteger(arg):
    number = int(arg)
    if number < 0:
         raise argparse.ArgumentTypeError("%d is negative." % number)
    else:
        return number


def featuresproportion(arg):
    proportion = float(arg)
    if proportion < 0 or proportion > 1:
        raise argparse.ArgumentTypeError("%d is out of range. It should be a non-negative floating point number less than or equal to 1." % proportion)
    else:
        return proportion


def featuresproportionprecision(arg):
    precision = float(arg)
    if precision <= 0 or precision >= 0.5:
        raise argparse.ArgumentTypeError("%d is out of range. It should be a positive floating point number less than 0.5." % precision)
    else:
        return precision


def openmsdirectorypath(arg):
    """Checks that the directory exists and contains an 'ExecutePipeline' binary file.
    """
    path = directorypath(arg)
    # unlike Windows, '.exe' is not a required extension for executable files on Unix-based systems
    if not os.path.exists(os.path.join(path, 'bin', 'ExecutePipeline%s' % '.exe' if os.name == 'nt' else '')):
        raise argparse.ArgumentTypeError('Executable file "ExecutePipeline" is not found in %r.' % path)
    return path

def getworkflowsettings():
    """Parses command line arguments and returns a FeatureDetectionSettings instance based on these values.
    """
    parser = argparse.ArgumentParser(prog='OpenMS feature detection settings tuner',
                                     description='The program takes a file with a TOPPAS workflow, which contains a FeatureDetectionMetabo node, '
                                                 'as input and adjusts its noise_threshold_int parameter so that the node produces '
                                                 'required amount of features from known LC-MS experimental data that are also provided to input.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--oms', type=openmsdirectorypath, dest='openms_base_dir_path', required=True, help='Path to an OpenMS installation directory.')
    parser.add_argument('--toppas', type=filepath, dest='workflow_file_path', required=True, help='Path to a *.toppas file with a TOPPAS workflow that contains a FetureFinderMetabo node.')
    parser.add_argument('--in', type=directorypath, dest='workflow_input_dir', required=True,
                        help='Path to a directory that contains files with centroided LC-MS data along with eponimous CSV-files that include lists of expected features for corresponding files.')

    parser.add_argument('--max_noise', type=nonnegativeinteger, dest='max_noise_level', default=10000000, help='Maximum acceptable value for the noise_threshold_int parameter of the FetureFinderMetabo algorithm.')
    parser.add_argument('--min_noise', type=nonnegativeinteger, dest='min_noise_level', default=0, help='Minimum acceptable value for the noise_threshold_int parameter of FetureFinderMetabo.')
    parser.add_argument('--mzt', type=nonnegativeinteger, dest='mz_tolerance_ppm', default=5, help='MZ tolerance for the feature detection procedure.')
    parser.add_argument('--match', type=featuresproportion, dest='required_expected_features_proportion', default=0.7,
                        help='A proportion of expected features, described by files in the directory specified by WORKFLOW_INPUT_DIR, that should be detected by FetureFinderMetabo.')
    parser.add_argument('--match_var', type=featuresproportionprecision, dest='features_proportion_precision', default=0.01,
                        help='An acceptable variation of calculated proportion of detected feaures when compared with REQUIRED_EXPECTED_FEATURES_PROPORTION.')

    settings = parser.parse_args()
    settings.workflow_output_dir = getworkflowoutputdirpath()

    return settings


def saveoutput(thread_number, mz_tolerance, noise_level):
    with open(OUTPUT_FILE_NAME, 'w') as output_file:
        loginfo('Saving tuning results to file %s' % os.path.abspath(OUTPUT_FILE_NAME))
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='#')  
        csv_writer.writerow(['thread_number', 'mz_tolerance', 'noise_threshold_int'])
        csv_writer.writerow([thread_number, mz_tolerance, noise_level])

    loginfo('Tuning results have been successfully saved')
    

def main():
    loginfo('Welcome to The TOPPAS Feature Detection Tuner v%s.\n' % __version__)
    workflow_settings = getworkflowsettings()
    input_files = getstandardfilenames(workflow_settings.workflow_input_dir)
    expected_features = {}
    for expected_features_file in input_files:
        expected_features[input_files[expected_features_file]] = getexpectedfeaturesfromfile(expected_features_file)

    result_noise_level = tuneworkflow(workflow_settings, expected_features)

    saveoutput(OPTIMAL_THREAD_COUNT, workflow_settings.mz_tolerance_ppm, result_noise_level)


if __name__ == "__main__":
   main()
