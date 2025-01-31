import os
import re
import logging
from scrub.utils import translate_results


def micro_filter_check(source_file, warning_line, warning_type, raw_valid_warning_types, checked_source_files):
    """This function checks to see if a warning has been marked as a false positive by the user.

    Inputs:
        - source_file: Absolute path to the source code file of interest [string]
        - warning_line: Line of interest of source code file [int]
        - warning_type: Full and accurate name of the check that should be ignored [string]
        - raw_valid_warning_types: List of lists containing valid types for each tool [list of list of strings]
        - checked_source_files: Dict of dicts with line_num:line_text data corresponding to previously read and stored
            scrub suppression lines. Dict is updated with new file dicts if a previously unopened source file
            is referenced via source_file parameter [dict of dict of int:string]

    Outputs:
        - ignore_line: Indicator if warning should be ignored [bool]
    """
    # Set the base string
    ignore_base = "scrub_ignore_warning"

    # Initialize the return value
    ignore_line = False

    # Get the types of interest
    tool_warning_types = []
    valid_warning_types = []

    for valid_type_set in raw_valid_warning_types:
        # build list of expected warning types to check lines to warn about entirely invalid suppression entries
        valid_warning_types = valid_warning_types + valid_type_set
        # build list of warning types for the current tool
        if warning_type in valid_type_set:
            tool_warning_types = tool_warning_types + valid_type_set

    # if p10 is already in the valid_warning_types, we're building a p10 output and want to catch those suppressions
    if 'p10' in valid_warning_types:
        tool_warning_types.append('p10')
    # else we want to add it to the valid warning types so we don't accidentally flag it as invalid, but we don't
    # want to suppress on it.
    else:
        valid_warning_types.append('p10')

    valid_warning_types = set(valid_warning_types)

    try:
        if source_file not in checked_source_files.keys():
            # Open the file of interest and read the lines
            file_lines = {}
            with open(source_file, 'r', errors='ignore') as fh:
                for line_num, line in enumerate(fh, start=1):
                    if (ignore_base in line.lower()) or ('@suppress' in line.lower()):
                        invalid_type = True
                        file_lines[line_num] = line
                        for check_type in valid_warning_types:
                            if check_type in line.lower():
                                invalid_type = False
                                break
                        if invalid_type:
                            logging.warning('\t\tNo valid tools found in suppression on line {} of file {}'
                                            .format(line_num, source_file))

            checked_source_files[source_file] = file_lines

        line = checked_source_files[source_file].get(warning_line) or ""

        # Check to see if the line should be filtered out
        if (ignore_base in line.lower()) or ('@suppress' in line.lower()):
            if any(check_type in line.lower() for check_type in tool_warning_types):
                ignore_line = True

                # Print a status message
                logging.debug('\tWarning removed - Warning has been marked as a false positive')
                logging.debug('\t\t%s', line)

    except IOError:
        logging.warning('\t\tMicro-filter warning')
        logging.warning('\t\tFile %s could not be found.', source_file)

    # Return value
    return ignore_line


def ignore_query_check(warning_tool, warning_query, ignore_queries_file):
    """This function checks if a result should be skipped based on the type of query.

    Inputs:
        - line: Line of interest from SCRUB results [string]
        - ignore_queries_file: Full path to the SCRUBExcludeQueries file [string]

    Outputs:
        - skip: Indicator if result should be filtered out [bool]
    """

    # Initialize the variables
    skip = False

    # Import the ignore data
    if os.path.isfile(ignore_queries_file):
        ignore_fh = open(ignore_queries_file, 'r')
        ignore_queries = ignore_fh.readlines()
        ignore_fh.close()

        # Iterate through every line of the ignore data
        for ignore_line in ignore_queries:
            # Split the line and store the values
            ignore_line_split = list(filter(None, re.split(':', ignore_line.strip())))
            ignore_tool = ignore_line_split[0].strip().lower()
            ignore_query = ignore_line_split[1].strip()

            # Determine if the ine should be skipped
            if (ignore_tool == warning_tool) and (ignore_query == warning_query):
                skip = True

                # Print a status message
                logging.debug('\tWarning removed - Warning generated by a filtered query')
                logging.debug('\t\t%s: %s', warning_tool, warning_query)

    return skip


def external_warning_check(warning_file, source_root):
    """This function checks to see if a warning originates outside the source code directory.

    Inputs:
        - warning_file:
        - source_root: Full path to the top level directory of the source code [string]

    Outputs:
        - skip: Indicator if result should be filtered out [bool]
    """

    # Check to see if the file exists outside the source root
    if not warning_file.startswith(source_root):
        skip = True

        # Print a status message
        logging.debug('\tWarning removed - Warning occurs in a file that is outside the source root')
        logging.debug('\t\t%s', warning_file)
    else:
        skip = False

    return skip


def baseline_filtering_check(warning_file, excluded_files):
    """This function checks to see if a warning occurs in a directory or file that should be ignored.

    Inputs:
        - warning_file: File of interest from warning data [string]
        - excluded_files: Set of files read from SCRUBAnalysisFilteringList file [set [string]]

    Outputs:
        - skip: Indicator if result should be filtered out [bool]
    """
    # Iterate through every line of the ignore data
    if warning_file in excluded_files:
        logging.debug('\tWarning removed - Warning occurs in a file that has been excluded from analysis')
        logging.debug('\t\t%s', warning_file)
        return True
    return False


def check_filtering_file(filtering_file, create):
    """This function checks the filtering file to see if it exists.

    Inputs:
        - filtering_file: Full path to the filtering file to be checked [string]
        - create: Flag to indicate if the file should be created if it doesn't exist [bool]
    """

    # Check to see if all the files exist
    if not os.path.isfile(filtering_file):
        logging.info('No %s file exists.', filtering_file)

        # Create the file if necessary
        if create:
            logging.info('\tCreating blank filtering file %s.', filtering_file)
            logging.info('\tPlease add filtering patterns to this file.')
            open(filtering_file, 'w+').close()


def duplicate_check(warning, warning_log):
    """This function checks to make sure that the warning has not been reported before.

    Inputs:
        - warning: current warning to be checked [string]
        - warning_log: log containing all warnings written previously [list of strings]

    Outputs:
        - skip: Indicator if result should be filtered out [bool]
    """

    # Initialize the variables
    skip = False

    # Check if the waring has been written out before
    if warning in warning_log:
        skip = True

    return skip


def filter_results(warning_list, output_file, filtering_file, ignore_query_file, source_root, enable_micro_filtering,
                   enable_external_warnings, valid_warning_types, checked_source_files):
    """This function performs the filtering, including all other filtering functions.

    Inputs:
        - input_files: List of absolute paths to the input file(s) of interest [list of string]
        - output_file: Absolute path to file where filtered results will be stored [string]
        - filtering_file: Absolute path to the SCRUBAnalayisFilteringList file [string]
        - ignore_query_file: Absolute path to the SCRUBExcludeQueries file [string]
        - source_root: Absolute path to the top level directory of the source code [string]
        - enable_micro_filtering: Flag to enable/disable micro filtering [logical]
        - enable_external_warnings: Flag to enable/disable external warnings [logical]
        - valid_warning_types: List of lists that contain valid warning type tags [list of lists]
        - checked_source_files: Dict of dicts with line_num:line_text data corresponding to previously read and stored
            scrub suppression lines. Dict is updated with new file dicts if a previously unopened source file
            is referenced via source_file parameter [dict of dict of int:string]

    Outputs:
        - output_file: All filtered results are written to the output_file
    """
    if checked_source_files is None:
        checked_source_files = {}

    # Initialize the variables
    filtered_warnings = []
    if output_file.endswith('p10.scrub'):
        valid_warning_types.append(['p10'])

    # Import the ignore data
    with open(filtering_file, 'r') as input_fh:
        excluded_files = set([x.strip() for x in input_fh.readlines()])

    # Print a log message
    logging.info('')
    logging.info('\tFiltering results...')
    logging.info('\t>> Executing command: filter_results.filter_results(<warning_list>, %s, %s, %s, %s, %r, %r)',
                 output_file, filtering_file, ignore_query_file, source_root, enable_micro_filtering,
                 enable_external_warnings)
    logging.info('\t>> From directory: %s', os.getcwd())

    # Update the source root to make it absolute
    source_root = os.path.abspath(source_root)

    # Iterate through every warning in the list
    for warning in warning_list:
        # Check to see if it should be ignored
        if baseline_filtering_check(warning['file'], excluded_files):
            continue

        # Check to see if the warning is external to the source directory
        if not enable_external_warnings \
                and external_warning_check(warning['file'], source_root):
            continue

        # Perform micro filtering checking
        if enable_micro_filtering \
                and micro_filter_check(warning['file'], warning['line'], warning['tool'],
                                       valid_warning_types, checked_source_files):
            continue

        # Check to see if the query should be ignore
        if ignore_query_check(warning['tool'], warning['query'], ignore_query_file):
            continue

        # If we made it here we want the warning.
        # Make the warning file path relative and append to filtered list
        warning['file'] = warning['file'].replace(os.path.normpath(source_root) + '/', '')
        filtered_warnings.append(warning)

    # Write out the results
    logging.info('\t>> Results filtered. Writing {}.'.format(output_file))

    translate_results.create_scrub_output_file(filtered_warnings, output_file)
