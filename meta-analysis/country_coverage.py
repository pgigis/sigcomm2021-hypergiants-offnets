import os
import json
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find country percentage of population coverage.')
    parser.add_argument('-i', '--input_folder',
                        help='The result input folder.',
                        type=str,
                        required=True)

    parser.add_argument('-a', '--apnic_file',
                        help='The APNIC file.',
                        type=str,
                        required=True)

    args = parser.parse_args()

    if args.input_folder[-1] != "/":
        args.input_folder += "/"

    if not os.path.exists('results'):
        os.makedirs('results')

    newFolder_path = "results/" + args.input_folder.split('/')[-2] + "/" + "country_coverage/"

    if not os.path.exists(newFolder_path):
        os.makedirs(newFolder_path)

    files_in_off_nets_folder = os.listdir(args.input_folder + "off-nets/")
    
    storeData = {}
    hg_keywords_l = list()

    for file in files_in_off_nets_folder:
        if '.txt' in file:
            hg_keyword = file.split('.')[0]
            hg_keywords_l.append(hg_keyword)

            if hg_keyword not in storeData:
                storeData[hg_keyword] = {}

            with open(args.input_folder + "off-nets/" + file, 'rt') as f:
                for line in f:
                    data = json.loads(line)
                    for ASN in data:
                        storeData[hg_keyword][str(ASN)] = None

    with open(args.apnic_file, 'rt') as f:
        apnic_data_json = json.load(f)
        for hg_keyword in hg_keywords_l:
            for ASN_offnet in storeData[hg_keyword]:
                with open(newFolder_path + hg_keyword + ".txt", 'wt') as fw:
                    for country in apnic_data_json:
                        coverage_perc = 0.0
                        for ASN_country in apnic_data_json[country]:
                           if str(ASN_country) in storeData[hg_keyword]:
                                coverage_perc += apnic_data_json[country][ASN_country]

                        fw.write("{0},{1}\n".format(country, coverage_perc))