import os
import json
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Displays results for an analysis.')
    parser.add_argument('-i', '--input_folder',
                        help='The result input folder.',
                        type=str,
                        required=True)

    parser.add_argument('-p', '--print_ases',
                        help='Print ASes list.',
                        type=bool,
                        required=False,
                        default=False)

    args = parser.parse_args()

    input_folder = args.input_folder
    if input_folder[-1] != "/":
        input_folder += "/"

    storeData = {}
    storeData['candidate'] = {}
    storeData['validated'] = {}

    hg_keywords_l = list()

    files_in_candidate_off_nets_folder = os.listdir(input_folder + "candidate_off-nets/")
  
    for file in files_in_candidate_off_nets_folder:
        if '.txt' in file:
            hg_keyword = file.split('.')[0]
            hg_keywords_l.append(hg_keyword)

            if hg_keyword not in storeData['candidate']:
                storeData['candidate'][hg_keyword] = set()

            with open(input_folder + "candidate_off-nets/" + file, 'rt') as f:
                for line in f:
                    data = json.loads(line)
                    storeData['candidate'][hg_keyword].add(data['ASN'])

    files_in_off_nets_folder = os.listdir(input_folder + "off-nets/")
  
    for file in files_in_off_nets_folder:
        if '.txt' in file:
            hg_keyword = file.split('.')[0]
            hg_keywords_l.append(hg_keyword)

            if hg_keyword not in storeData['validated']:
                storeData['validated'][hg_keyword] = set()

            with open(input_folder + "off-nets/" + file, 'rt') as f:
                for line in f:
                    data = json.loads(line)
                    storeData['validated'][hg_keyword].update(list(data.keys()))

    for hg_keyword in hg_keywords_l:
        print("\nHG Keyword: '{}'".format(hg_keyword))
        print("Found Candidate Off-nets (only certificates) in {0} ASes.".format(len(storeData['candidate'][hg_keyword])))
        print("Found Off-nets (validated with HTTP(s) headers) in {0} ASes.".format(len(storeData['validated'][hg_keyword])))
        
        if args.print_ases:
            print("ASes for Candidate Off-nets:")
            print("{}".format(", ".join( ["AS" + str(ASN) for ASN in storeData['candidate'][hg_keyword]])))
            print('- - -')
            print("ASes for Validated Off-nets:")
            print("{}".format(", ".join( ["AS" + str(ASN) for ASN in storeData['validated'][hg_keyword]])))
        print("-------------------------------------------------------------------")