from FinalLinksCode import addAtlasNamestoCSV as fac
import sys

if __name__ == '__main__':
    """
    in_file1: File that contains all the links of the study in question
    about consistency. It contains link name in each line.
    in_file2: File that contains all the consistent links for all studies.

    Usage:
    ------
    >>> python3 check_number_of_inconsistencies_driver.py csv_input/links_file_study28 csv_input/consistencies_file
    """
    in_file1 = sys.argv[1]
    in_file2 = sys.argv[2]

    print('Number of Consistencies = %d'%
          fac.check_number_of_consistencies(in_file1, in_file2))
