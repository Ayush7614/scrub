===============
Troubleshooting
===============

SCRUB produces a large number of intermediary files in an effort to make debugging errors easier. The following
sections attempt to facilitate this process by providing the user with a trace of the output file production, a
simplified programmatic flow, and a high level description of each routine.

Common Error Messages
#####################
SCRUB performs different levels of fault handling and provides status messages to the user. A list of error messages,
their origin, and recommended responses is provided below.

+-------------------------------+-----------------------+--------------------------------------------------------------+
| Warning Message               | Message Origin        | Recommended Action                                           |
+===============================+=======================+==============================================================+
| CommandExecutionError         | execute_command       | Some error has occurred when trying to execute a tool        |
|                               |                       | specific command. Review the referenced log file for         |
|                               |                       | detailed debugging information.                              |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| Invalid micro-filter type     | do_filtering          | Micro-filtering was attempted in the source code, but an     |
|                               |                       | invalid micro filtering type was used. Review the source     |
|                               |                       | file and line to update the micro-filtering tag              |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| Could not generate output     | do_filtering          | An issue occurred when trying to generate the output file,   |
| file                          |                       | check the log file .scrub/log_files/filtering.log for more   |
|                               |                       | information.                                                 |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| Output file is empty          | check_output_files    | SCRUB has detected an empty output file that normally should |
|                               |                       | not be empty. Review the tool log to make sure there are no  |
|                               |                       | issues.                                                      |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| A SCRUB warning is missing    | get_scrub_warnings    | An issue was encountered when trying to convert SCRUB        |
| some results metadata         |                       | results into SARIF. Please review the file to identify the   |
|                               |                       | malformed line.                                              |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| Failed to parse file, SARIF   | translate_results     | The SARIF file cannot be parsed because the SARIF version    |
| schema version does not match |                       | being used is not supported by SCRUB. Output to another      |
| SCRUB supported versions      |                       | SARIF version if possible.                                   |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| Invalid XML file.             | do_collaborator       | The XML file created by do_collaborator.py is malformed.     |
| Collaborator upload could     |                       | Please retry analysis.                                       |
| not be completed.             |                       |                                                              |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| Collaborator upload could not | do_collaborator       | An issue occurred when trying to perform an upload to        |
| be performed. Please see log  |                       | Collaborator. Review the log file for more information.      |
| file for more information.    |                       |                                                              |
+-------------------------------+-----------------------+--------------------------------------------------------------+
| A SCRUB error has occurred.   | scrubme               | A Python error has occurred during the execution of SCRUB.   |
| Please see log file for more  |                       | Please review the log file and submit a GitHub issue if      |
| information.                  |                       | necessary.                                                   |
+-------------------------------+-----------------------+--------------------------------------------------------------+
