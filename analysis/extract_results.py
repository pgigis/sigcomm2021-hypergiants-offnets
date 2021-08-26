import os
import pytricia
import gzip
import json
import pprint
import re

def cloudflare_exclude(dns_names):
    exclude = False
    if 'sni.cloudflaressl.com' in dns_names:
        exclude = True
    for entry in dns_names:
        matches = re.match("ssl[0-9]*.cloudflare.com", entry)
        if matches is not None:
            exclude = True
    if exclude:
        return True
    else:
        return False


# Load the IP-to-AS mapping file
def load_pytricia_tree(filename):
    pyt = pytricia.PyTricia()
    with open(filename, 'rt') as f:
        data = json.load(f)
    for prefix in data:
        pyt[prefix] = data[prefix]
    return pyt

def load_prt_records(filename):
    ips = dict()
    with gzip.open(filename, 'rt') as f:
        for line in f:
            ips[line.split(',')[0]] = None
    return ips

# Load the ASN full names
def load_the_ASN_fullNames(filename):
    asns_fnames = dict()
    with open(filename, 'rt') as f:
        for line in f:
            line_ = line.rstrip()
            asn = int(line_.split(' ')[0])
            fname = ' '.join(line_.split(' ')[1:])
            asns_fnames[asn] = fname
    return asns_fnames


def load_the_headers(filename):
    http_headers = dict()
    with gzip.open(filename, 'rt') as f:
        for line in f:
            ip, hg, header = line.rstrip().split('\t')
            http_headers[ip] = hg.lower()
    return http_headers


def load_hypergiant_ases(filename):
    hg_ases = dict()
    try: 
        with open(filename, 'rt') as f:
            data = json.load(f)
            for hypergiant in data:
                    hg_ases[hypergiant] = list(map(int, data[hypergiant]['asns']))
    except:
        print("Couldn't load \"{}\".".format(filePath))
        return None

    return hg_ases



def main():

    ip2as = load_pytricia_tree("/home/extra_disk/data/download_2021/2021_01_db.json")
    asnFullNames = load_the_ASN_fullNames("/home/extra_disk/data/sigcomm2021-offnets-artifacts/datasets/asn_names/asn-names.txt")

    http_header = load_the_headers("mapped_header_names_2021-01-11-1610327300-http_get_80.json.gz")
    https_header = load_the_headers("mapped_header_names_2021-01-11-1610327088-https_get_443.json.gz")

    HG_ASes = load_hypergiant_ases("/home/extra_disk/data/download_2021/2021_01_hypergiants_asns.json")

    ptr_records = load_prt_records("/home/extra_disk/data/download_2021/2021-01-13-1610496291-rdns_translated.json.gz")

    path_on_nets = "results/active_11-01-2021/on-nets/"
    path_off_nets = "results/active_11-01-2021/candidate_off-nets/"
    files_on_nets = os.listdir(path_on_nets)

    final_path = "results/active_11-01-2021/final/"
    if not os.path.exists(final_path):
        os.makedirs(final_path)

    on_net_asns_set = dict()
    candidate_off_net_asns_set = dict()

    ### Only Certificates
    for file in files_on_nets:
        if '.txt' in file:
            hg_keyword = file.split('.')[0]
            on_net_asns_set[hg_keyword] = set()
            candidate_off_net_asns_set[hg_keyword] = set()

            with open(path_on_nets + file, 'rt') as f:
                for line in f:
                    data_json = json.loads(line)
                    on_net_asns_set[hg_keyword].add(data_json['ASN'])
            

                    if hg_keyword in HG_ASes:
                        if set(on_net_asns_set[hg_keyword]).issubset(set(HG_ASes[hg_keyword])) == False:
                            print("Error On-nets ", str(hg_keyword), str(on_net_asns_set[hg_keyword]))

            
            with open(path_off_nets + file, 'rt') as f:
                for line in f:
                    data_json = json.loads(line)

                    if hg_keyword == "cloudflare" and cloudflare_exclude(data_json['dns_names']):
                        continue
                    candidate_off_net_asns_set[hg_keyword].add(data_json['ASN'])

            toRemove = list()
            all_other_HGs = set()
            for hg_ in HG_ASes:
                if hg_keyword == hg_:
                    continue
                else:
                    all_other_HGs.update(HG_ASes[hg_])

            other_Hgs_off_net = list()
            for candidate_asn_off_net in candidate_off_net_asns_set[hg_keyword]:
                if candidate_asn_off_net in all_other_HGs:
                    other_Hgs_off_net.append(candidate_asn_off_net)
                    toRemove.append(candidate_asn_off_net)

            for rem_ in toRemove:
                candidate_off_net_asns_set[hg_keyword].remove(rem_)

            with open(final_path + hg_keyword + "_only_certificates.txt", 'wt') as fw:
                fw.write("# Total offNet {}\n".format(len(candidate_off_net_asns_set[hg_keyword])))
                fw.write("# Total onNet {}\n".format(len(on_net_asns_set[hg_keyword])))
                fw.write("# Total other HG ASNs {}\n".format(len(other_Hgs_off_net)))

                # Write the onNet ASNs
                fw.write("# BEGIN onNet\n")
                for onnet_asn in on_net_asns_set[hg_keyword]:
                    asn_fname = ""
                    if onnet_asn in asnFullNames:
                        asn_fname = asnFullNames[onnet_asn]
                    fw.write("{0} - {1}\n".format(onnet_asn, asn_fname))
                fw.write("# END onNet\n")

                fw.write("# BEGIN offNet\n")
                for offnet_asn in candidate_off_net_asns_set[hg_keyword]:
                    asn_fname = ""
                    if offnet_asn in asnFullNames:
                        asn_fname = asnFullNames[offnet_asn]
                    fw.write("{0} - {1}\n".format(offnet_asn, asn_fname))
                fw.write("# END offNet\n")

                fw.write("# BEGIN Other-HG-ASNs\n")
                for other_asn in other_Hgs_off_net:
                    asn_fname = ""
                    if other_asn in asnFullNames:
                        asn_fname = asnFullNames[other_asn]
                    fw.write("{0} - {1}\n".format(other_asn, asn_fname))
                fw.write("# END Other-HG-ASNs\n")


    # ----------------------------------------------------------------------------------
    ### HEADERS VALIDATION

    onNets = dict()
    onNets['or'] = dict()
    onNets['and'] = dict()

    offNets = dict()
    offNets['or'] = dict()
    offNets['and'] = dict()

    

    otherHG_or = dict()
    otherHG_and = dict()

    for file in files_on_nets:
        if '.txt' in file:
            hg_keyword = file.split('.')[0]
            otherHeader = set()
            onNets['or'][hg_keyword] = set()
            onNets['and'][hg_keyword] = set()
            
            with open(path_on_nets + file, 'rt') as f:
                for line in f:
                    data_json = json.loads(line)

                    # Netflix
                    if hg_keyword == "netflix":
                        if data_json['ip'] in ptr_records:
                            onNets['or'][hg_keyword].add(data_json['ASN'])

                    # HTTP and HTTPs agree
                    if data_json['ip'] in http_header and data_json['ip'] in https_header:
                        if http_header[data_json['ip']] == hg_keyword and https_header[data_json['ip']] == hg_keyword:
                            onNets['and'][hg_keyword].add(data_json['ASN'])

                    # HTTP or HTTPs agree
                    if data_json['ip'] in http_header:
                        if http_header[data_json['ip']] == hg_keyword:
                            onNets['or'][hg_keyword].add(data_json['ASN'])
                    
                    if data_json['ip'] in https_header:
                        if https_header[data_json['ip']] == hg_keyword:
                            onNets['or'][hg_keyword].add(data_json['ASN'])

            offNets['or'][hg_keyword] = set()
            offNets['and'][hg_keyword] = set()

            with open(path_off_nets + file, 'rt') as f:
                for line in f:
                    data_json = json.loads(line)

                    # Exclude Cloudflare
                    if hg_keyword == "cloudflare" and cloudflare_exclude(data_json['dns_names']):
                        continue

                    # Netflix
                    if hg_keyword == "netflix":
                        if data_json['ip'] in ptr_records:
                            offNets['or'][hg_keyword].add(data_json['ASN'])
                    
                    b_http_headers_match = False
                    if data_json['ip'] in http_header:
                        if hg_keyword == http_header[data_json['ip']]:
                            b_http_headers_match = True
                        else:
                           otherHeader.add(data_json['ASN'])

                    b_https_headers_match = False
                    if data_json['ip'] in https_header:
                        if hg_keyword == https_header[data_json['ip']]:
                            b_https_headers_match = True
                        else:
                            otherHeader.add(data_json['ASN'])

                    if (b_http_headers_match == True and b_https_headers_match == True):
                        offNets['and'][hg_keyword].add(data_json['ASN'])

                    if (b_http_headers_match == True or b_https_headers_match == True):
                        offNets['or'][hg_keyword].add(data_json['ASN'])
            
            toRemove = list()
            all_other_HGs = set()
            for hg_ in HG_ASes:
                if hg_keyword == hg_:
                    continue
                else:
                    all_other_HGs.update(HG_ASes[hg_])

            other_HGs_offNet = dict()
            other_HGs_offNet['or'] = set()
            for candidate_asn_off_net in offNets['or'][hg_keyword]:
                if candidate_asn_off_net in all_other_HGs:
                    other_HGs_offNet['or'].add(candidate_asn_off_net)
                    toRemove.append(candidate_asn_off_net)

            for rem_ in toRemove:
                offNets['or'][hg_keyword].remove(rem_)

            
            toRemove = list()
            other_HGs_offNet['and'] = set()
            for candidate_asn_off_net in offNets['and'][hg_keyword]:
                if candidate_asn_off_net in all_other_HGs:
                    other_HGs_offNet['and'].add(candidate_asn_off_net)
                    toRemove.append(candidate_asn_off_net)

            for rem_ in toRemove:
                other_HGs_offNet['and'].remove(rem_)

            with open(final_path + hg_keyword + "_http_and_https.txt", 'wt') as fw:
                fw.write("# Total offNet {}\n".format(len(offNets['and'][hg_keyword])))
                fw.write("# Total onNet {}\n".format(len(onNets['and'][hg_keyword])))
                fw.write("# Total other HG ASNs {}\n".format(len(other_HGs_offNet['and'])))

                # Write the onNet ASNs
                fw.write("# BEGIN onNet\n")
                for onnet_asn in onNets['and'][hg_keyword]:
                    asn_fname = ""
                    if onnet_asn in asnFullNames:
                        asn_fname = asnFullNames[onnet_asn]
                    fw.write("{0} - {1}\n".format(onnet_asn, asn_fname))
                fw.write("# END onNet\n")

                fw.write("# BEGIN offNet\n")
                for offnet_asn in offNets['and'][hg_keyword]:
                    asn_fname = ""
                    if offnet_asn in asnFullNames:
                        asn_fname = asnFullNames[offnet_asn]
                    fw.write("{0} - {1}\n".format(offnet_asn, asn_fname))
                fw.write("# END offNet\n")

                fw.write("# BEGIN Other-HG-ASNs\n")
                for other_asn in other_HGs_offNet['and']:
                    asn_fname = ""
                    if other_asn in asnFullNames:
                        asn_fname = asnFullNames[other_asn]
                    fw.write("{0} - {1}\n".format(other_asn, asn_fname))
                fw.write("# END Other-HG-ASNs\n")

            with open(final_path + hg_keyword + "_http_or_https.txt", 'wt') as fw:
                fw.write("# Total offNet {}\n".format(len(offNets['or'][hg_keyword])))
                fw.write("# Total onNet {}\n".format(len(onNets['or'][hg_keyword])))
                fw.write("# Total other HG ASNs {}\n".format(len(other_HGs_offNet['or'])))
                fw.write("# Total other HG Headers {}\n".format(len(otherHeader)))

                # Write the onNet ASNs
                fw.write("# BEGIN onNet\n")
                for onnet_asn in onNets['or'][hg_keyword]:
                    asn_fname = ""
                    if onnet_asn in asnFullNames:
                        asn_fname = asnFullNames[onnet_asn]
                    fw.write("{0} - {1}\n".format(onnet_asn, asn_fname))
                fw.write("# END onNet\n")

                fw.write("# BEGIN offNet\n")
                for offnet_asn in offNets['or'][hg_keyword]:
                    asn_fname = ""
                    if offnet_asn in asnFullNames:
                        asn_fname = asnFullNames[offnet_asn]
                    fw.write("{0} - {1}\n".format(offnet_asn, asn_fname))
                fw.write("# END offNet\n")

                fw.write("# BEGIN Other-HG-ASNs\n")
                for other_asn in other_HGs_offNet['or']:
                    asn_fname = ""
                    if other_asn in asnFullNames:
                        asn_fname = asnFullNames[other_asn]
                    fw.write("{0} - {1}\n".format(other_asn, asn_fname))
                fw.write("# END Other-HG-ASNs\n")

                fw.write("# BEGIN other HG Headers\n")
                for excluded_asn in otherHeader:
                    asn_fname = ""
                    if excluded_asn in asnFullNames:
                        asn_fname = asnFullNames[excluded_asn]
                    fw.write("{0} - {1}\n".format(excluded_asn, asn_fname))
                fw.write("# END other HG Headers\n")
main()