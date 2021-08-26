import os
import json
import gzip
import argparse

from lib.helpers import createPath 

def load_header_fingerprints(filename):
    returnDict = dict()
    try:
        with gzip.open(filename, 'rt') as f:
            for line in f:
                line_splitted = line.rstrip().split('\t')
                returnDict[line_splitted[0]] = line_splitted[1].lower()
    except:
        print("Couldn't load/process header file \"{}\"".format(filename))
        return None
    return returnDict


def process_offnets(folderName, http_fingerprints, https_fingerprints, filePathToStoreResults):
    files = os.listdir(folderName)
    hg_keywords_l = list()
    for file in files:
        if '.txt' in file:
            hg_keywords_l.append(file.split('.')[0])

    for hg_keyword in hg_keywords_l:
        storeData = dict()

        with open(folderName + hg_keyword + ".txt", 'rt') as f:
            for line in f:
                data = json.loads(line)

                if data['ip'] in http_fingerprints and data['ip'] in https_fingerprints:
                    if hg_keyword == http_fingerprints[data['ip']]:
                        if data['ASN'] not in storeData:
                            storeData[data['ASN']] = list()
                        storeData[data['ASN']].append(data['ip'])

        print("Inferred \"{0}\" off-nets in {1} ASes".format(hg_keyword, len(storeData)))
        with open(filePathToStoreResults + hg_keyword + ".txt", 'wt') as f:
            json.dump(storeData, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find off-nets per hypergiant.')
    
    parser.add_argument('-o', '--off_netsFolder',
                        help='The input on-nets folder.',
                        type=str,
                        required=True),
    parser.add_argument('-http', '--http_fingerprints',
                        type=str,
                        help="The input file with the HTTP fingerprints.",
                        required=True)
    parser.add_argument('-https', '--https_fingerprints',
                        type=str,
                        help="The input file with the HTTP fingerprints.",
                        required=True)

    args = parser.parse_args()


    filePathToStoreResults = "/".join(args.off_netsFolder.split("/")[:-2]) + "/off-nets/"
    createPath(filePathToStoreResults)

    http_fingerprints = load_header_fingerprints(args.http_fingerprints)
    if http_fingerprints is None:
        exit()

    https_fingerprints = load_header_fingerprints(args.https_fingerprints)
    if https_fingerprints is None:
        exit()

    process_offnets(args.off_netsFolder, http_fingerprints, https_fingerprints, filePathToStoreResults)