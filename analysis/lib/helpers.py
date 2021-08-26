import os
import json
import pytricia

# Load the IP-to-AS mapping file
def load_ip_to_as_mapping(filename):
    pyt = pytricia.PyTricia()
    try:
        with open(filename, 'rt') as f:
            data = json.load(f)
        for prefix in data:
            pyt[prefix] = data[prefix]
    except:
        print("Couldn't load/process IP-to-AS mapping file \"{}\"".format(filename))
        return None
    return pyt


# Create path
def createPath(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Load and the config file
def load_config_file(configFile):
    hg_keyword_to_hg_ases_key = dict()
    try:
        with open(configFile, 'rt') as f:
            for line in f:
                data = json.loads(line.rstrip())
                hg_keyword_to_hg_ases_key[data['hypergiant-keyword']] = data['hypergiant-ases-key']
    except:
        print("Couldn't load/process config file \"{}\"".format(configFile))
        return None
    return hg_keyword_to_hg_ases_key


def load_hypergiant_ases(filename):
    hg_ases = dict()
    try: 
        with open(filename, 'rt') as f:
            data = json.load(f)
            for hypergiant in data:
                    hg_ases[hypergiant] = data[hypergiant]['asns']
    except:
        print("Couldn't load \"{}\".".format(filePath))
        return None

    return hg_ases


def process_configuration_file(configuration_input, hg_ases):
    # Check if for all keywords, a hypergiant-ases-key in the hypergiant ASes file.
    for input_ in configuration_input:  
        if configuration_input[input_] not in hg_ases:
            print("-> hypergiant-ases-key \"{}\" not found.".format(configuration_input[input_] ))
            print("Available \"hypergiant-ases-key\" keys:\n{}".format(list(hg_ases.keys())))
            return None
    
    hg_asn_to_hg_keywords = dict()      
    for hg_keyword in configuration_input:
        for ASN in hg_ases[configuration_input[hg_keyword]]:
            if int(ASN) not in hg_asn_to_hg_keywords:
                hg_asn_to_hg_keywords[int(ASN)] = set()
            hg_asn_to_hg_keywords[int(ASN)].add(hg_keyword)
    
    return hg_asn_to_hg_keywords