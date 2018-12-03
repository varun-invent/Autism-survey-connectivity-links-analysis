from FinalLinksCode import addAtlasNamestoCSV as aa
import argparse

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--function", required=False,
                help="Function to use")
ap.add_argument("-i", "--in_file", required=False,
                help="Input file path")
ap.add_argument("-n", "--node1_idx_reverse", required=False,
                help="comma seperated values of reverse node index")
ap.add_argument("-e", "--src_equals_dest_idx", required=False,
                help="src_equals_dest_idx")


args = vars(ap.parse_args())

in_file = args["in_file"]

if args["node1_idx_reverse"] != None:
    node1_idx_reverse = list(map(int, args["node1_idx_reverse"].split(',')))
else:
    node1_idx_reverse = [2,3,0,1]
if args["src_equals_dest_idx"] != None:
    src_equals_dest_idx = int(args["src_equals_dest_idx"])
else:
    src_equals_dest_idx = 8


if args["function"] == 'ddl':
    # Utiliy script use the delete duplicate links from a CSV for the purpose
    # of making it useful for cytoscape.
    aa.delete_duplicate_links(in_file, node1_idx_reverse = node1_idx_reverse ,\
                                    src_equals_dest_idx = src_equals_dest_idx)
else:
    print('Wrong input function')
