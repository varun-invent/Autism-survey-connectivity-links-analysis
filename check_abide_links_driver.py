from FinalLinksCode import addAtlasNamestoCSV as fac
import sys

if __name__ == '__main__':
    """
    in_file1: File that contains all the links of the study in question
    about consistency. It contains link name in each line.
    in_file2: File that contains all the consistent links for all studies.

    Usage:
    ------
    >>> python3 check_abide_links_driver.py csv_input/in_file_abide_distribution.csv
    """
    in_file = sys.argv[1]
    all_links_col_idx = [0,1]
    consistent_links_col_idx = [2]
    paperID_participant_col_idx = [3,5]


    fac.find_ABIDE_links(in_file, all_links_col_idx, consistent_links_col_idx, paperID_participant_col_idx)
