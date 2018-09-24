from FinalLinksCode import addAtlasNamestoCSV as fac
import sys

if __name__ == '__main__':
    """
    This can be used to check the consistencies/inconsistencies per study
    in_file1: File that contains all the links of all studies. It contains study
    ID and link name in each line.
    in_file2: File that contains all the consistent links for all studies.

    Usage:
    ------
    OLD >>> python3 check_number_of_consistencies_driver.py csv_input/links_file_study28 csv_input/consistencies_file
    NEW >>> python3 check_number_of_consistencies_driver.py csv_input/AAL_all_links.csv csv_input/AAL_consistent_links.csv

    """
    in_file1 = sys.argv[1]
    in_file2 = sys.argv[2]

    # Old
    # print('Number of Consistencies = %d'%
    #       fac.check_number_of_consistencies(in_file1, in_file2))

    # New
    fac.check_number_of_consistencies_per_study(in_file1, in_file2)


# NUmber of consistencies with study 28 came out to be 12
