import os
import json
import pprint
import argparse
import pytricia

from lib.helpers import load_ip_to_as_mapping, createPath, load_config_file, load_hypergiant_ases, process_configuration_file


def process_ee_certs(inputFile, ip_to_as, hg_asn_to_hg_keywords, filePathToStoreResults):
    openFiles_l = dict()
    hg_keywords_l = {v for v_list in hg_asn_to_hg_keywords.values() for v in v_list}
    for hg_keyword in hg_keywords_l:
        filePath = filePathToStoreResults + hg_keyword + ".txt"
        openFiles_l[hg_keyword] = open(filePath, 'wt')

    with open(inputFile, 'rt') as f:
        for line in f:
            data = json.loads(line)

            for ip in data:
                asns = list()
                try:
                    asns = ip_to_as[ip]
                except:
                    pass
            
            keywords_matched = None
            foundASN = None
            # Iterate over all ASNs of the IP-to-AS mapping (MOAS)
            for asn in asns:
                # Check if the ASN match to any of the hypergiant ASes
                if asn in hg_asn_to_hg_keywords: 
                    keywords_matched = hg_asn_to_hg_keywords[asn]
                    foundASN = asn
                    break

            if keywords_matched is not None:
                if 'subject' in data[ip]:
                    if 'organization' in data[ip]['subject']:
                        organization_value = ""
                        for item in data[ip]['subject']['organization']:
                            if item is not None:
                                organization_value += item.lower() + " "
                        for keyword in keywords_matched:
                            if keyword in organization_value:
                                storeJSON = { 
                                                "ip" : ip,
                                                "ASN" : foundASN,
                                                "dns_names" : data[ip]['dns_names'],
                                                "subject:organization" : organization_value
                                            }
                                openFiles_l[keyword].write("{}\n".format(json.dumps(storeJSON)))    

    for file in openFiles_l:
        openFiles_l[file].close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process hypergiant on-net certificates.')
    
    parser.add_argument('-s', '--hypergiantASesFile',
                        help='The input hypergiant ASes file.',
                        type=str,
                        required=True)
    parser.add_argument('-i', '--inputFile',
                        type=str,
                        help="The input file with EE certificates.",
                        required=True)
    parser.add_argument('-c', '--configFile',
                        type=str,
                        help="The input configuration file.",
                        required=True)
    parser.add_argument('-a', '--ipToASFile',
                        type=str,
                        help="The input IP-to-AS file.",
                        required=True)

    args = parser.parse_args()

    # Create on-nets folder
    filePathToStoreResults = "/".join(args.inputFile.split("/")[:-1]) + "/on-nets/"
    createPath(filePathToStoreResults)

    # Load the IP-to-AS mapping
    ip_to_as = load_ip_to_as_mapping(args.ipToASFile)

    # Load the Hypergiant ASes
    hg_ases = load_hypergiant_ases(args.hypergiantASesFile)
    if hg_ases is None:
        exit()

    # Load the config file
    configuration_input = load_config_file(args.configFile)
    if configuration_input is None:
        exit()

    # Check if config file is valid and return a map between HG ASes and HG keywords
    hg_asn_to_hg_keywords = process_configuration_file(configuration_input, hg_ases)
    if hg_asn_to_hg_keywords is None:
        exit()
    
    process_ee_certs(args.inputFile, ip_to_as, hg_asn_to_hg_keywords, filePathToStoreResults)


