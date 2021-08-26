import os
import csv
import json
import argparse
import collections

def read_org_info(filename):
    orgid_to_countries = {}
    orgid_to_asns = collections.defaultdict(set)
    count = 0
    with open(args.as2org, 'r') as f1:
        line = f1.readline()
        while line:
            data = []
            while line.startswith('#'):
                line = f1.readline()
                if not line:
                    break
            while not line.startswith('#'):
                data.append(line)
                line = f1.readline()
                if not line:
                    break
            reader = csv.reader(data, delimiter='|')
            for row in reader:
                if count == 0:
                    orgid_to_countries[row[0]] = row[3]
                elif count == 1:
                    orgid_to_asns[row[3]].add(row[0])
            count += 1
            
    asn_to_country_caida = {}
    for key in orgid_to_countries.keys():
        for asn in orgid_to_asns[key]:
            asn_to_country_caida[asn] = orgid_to_countries[key]

    return asn_to_country_caida


def read_country_to_continent(filename="../datasets/country_to_continent/country_to_continent.txt"):
    coutnry_to_continent_d = dict()
    with open(filename, 'r') as f2:
        next(f2)
        reader = csv.reader(f2, delimiter=',')
        coutnry_to_continent_d = { key: value for key, value in reader }
    return coutnry_to_continent_d


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group hypergiant off-net ASes per continent.')
    parser.add_argument('-i', '--input_folder',
                        help='The result input folder.',
                        type=str,
                        required=True)

    parser.add_argument('-c', '--as2org',
                        help='The CAIDA AS-to-Organization info file.',
                        type=str,
                        required=True)

    args = parser.parse_args()

    if args.input_folder[-1] != "/":
        args.input_folder += "/"

    asn_to_country_caida_d = read_org_info(args.as2org)
    country_to_continent_d = read_country_to_continent()

    files_in_off_nets_folder = os.listdir(args.input_folder + "off-nets/")
    
    storeData = {}
    hg_keywords_l = list()

    for file in files_in_off_nets_folder:
        if '.txt' in file:
            hg_keyword = file.split('.')[0]
            hg_keywords_l.append(hg_keyword)

            if hg_keyword not in storeData:
                storeData[hg_keyword] = {
                    "EU": set(),
                    "AF": set(),
                    "SA": set(),
                    "AS": set(),
                    "NA": set(),
                    "OC": set()
                }

            with open(args.input_folder + "off-nets/" + file, 'rt') as f:
                for line in f:
                    data = json.loads(line)
                    for ASN in data:
                        if ASN in asn_to_country_caida_d:
                            cc = asn_to_country_caida_d[ASN]
                            if cc in country_to_continent_d:
                                continent_ = country_to_continent_d[cc]
                                storeData[hg_keyword][continent_].add(ASN)
    newFolder_path = "results/" + args.input_folder.split('/')[-2] + "/" + "offnets_to_continents/"

    if not os.path.exists(newFolder_path):
        os.makedirs(newFolder_path)

    for hg_keyword in hg_keywords_l:
        with open(newFolder_path + hg_keyword + ".txt", 'wt') as fw:
            for continent in storeData[hg_keyword]:
                fw.write("{0}: {1} ASes\n".format(continent, len(storeData[hg_keyword][continent])))
            fw.write('# # #\n')
            for continent in storeData[hg_keyword]:
                fw.write("{0}: {1} \n- - - \n".format(continent, ", ".join(["AS" + str(ASN) for ASN in storeData[hg_keyword][continent]])))