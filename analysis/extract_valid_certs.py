import os
import json
import pprint
import hashlib
import argparse
import binascii
import datetime

from datetime import timezone
from lib.helpers import createPath

week = 60*60*24*7

# Load the active scan dataset
def load_active_scan_files(folderPath):
    files_l = list()
    folders = os.listdir(folderPath)
    for folder in folders:
        if 'b_' not in folder:
            continue
        files = os.listdir(folderPath + "/" + folder)
        for file in files:
            if 'certs.txt' == file:
                filepath = folderPath + folder + "/" + file
                files_l.append(filepath)
    return files_l


def hash_cert(pem):
    pem_to_hash = pem.replace('\n','').replace('-----BEGIN CERTIFICATE-----','').replace('-----END CERTIFICATE-----','')
    pem_to_hash += "=" * ((4 - len(pem_to_hash) % 4) % 4)
    pem_decode = binascii.a2b_base64(pem_to_hash)
    hash_object = hashlib.sha1(pem_decode)
    return hash_object.hexdigest(), pem_to_hash


def parse_date(value):
    if 'T' in value:
        return datetime.datetime.strptime(value.split('T')[0], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()
    else:
        return datetime.datetime.strptime(value.split(' ')[0], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()


def is_expired(not_after, not_before, snapshot_date_timestamp):
    if snapshot_date_timestamp <= (not_after + week) and (not_before - week) <= snapshot_date_timestamp:
        return False
    else:
        return True


def is_valid_cert(certificates_l, ccadb_hashes, snapshot_timestamp):
    # Check if root certificate in ccadb
    if 'pem' in certificates_l[-1]:
        certHashed, rawPem = hash_cert(certificates_l[-1]['pem'])
        if certHashed not in ccadb_hashes:
            return None

    ee_cert = None
    for certificate in certificates_l:
        if 'not_before' in certificate and 'not_after' in certificate:
            if is_expired(parse_date(certificate['not_after']), parse_date(certificate['not_before']), snapshot_timestamp):
                return None

        if 'basic_constraints' in certificate:
            if 'is_ca' in certificate['basic_constraints']:
                if certificate['basic_constraints']['is_ca'] == False:
                    if 'dns_names' in certificate:
                        if len(certificate['dns_names']) > 0:
                            if 'is_self_signed' in certificate:
                                if certificate['is_self_signed'] == False:
                                    ee_cert = certificate
    return ee_cert


def process_active_scan_data(files, ccadb_hashes, snapshot_timestamp, resultPath):
    count = 0
    total_files = len(files_l)

    fileToWrite = open(resultPath + "/ee_certs.txt", 'wt')

    for file in files_l:
        count += 1
        print("Processing {0}/{1} file \"{2}\"".format(count, total_files, file))
        
        with open(file, 'rt') as f:
            for line in f:
                try: 
                    data = json.loads(line.rstrip())
                except:
                    print("Couldn't load line {}".format(line))
                    continue

                for ip in data:
                    if 'certificates' in data[ip]:
                        ee_cert = is_valid_cert(data[ip]['certificates'], ccadb_hashes, snapshot_timestamp)
                        if ee_cert is not None:
                            fileToWrite.write("{}\n".format(json.dumps({ ip : ee_cert })))
    fileToWrite.close()


def process_rapid7_scan_data(files, ccadb_hashes, snapshot_timestamp, resultPath):
    count = 0
    total_files = len(files_l)

    fileToWrite = open(resultPath + "/ee_certs.txt", 'wt')

    with open(file, 'rt') as f:
        for line in f:
            try:
                data = json.loads(line.rstrip())
            except:
                print("Couldn't load line {}".format(line))
                continue

            for ip in data:
                if 'certificates' in data[ip]:
                    ee_cert = is_valid_cert(data[ip]['certificates'], ccadb_hashes, snapshot_timestamp)
                    if ee_cert is not None:
                        fileToWrite.write("{}\n".format(json.dumps({ ip : ee_cert })))
    fileToWrite.close()


def load_ccadb_hashes(filePath="../datasets/tls_scans/ccadb/cert_hashes_ccadb.txt"):
    ccadb_hashes = dict()
    with open(filePath, 'rt') as f:
        for line in f:
            ccadb_hashes[line.rstrip()] = None
    return ccadb_hashes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract End-Entity (EE) certificates.')
    parser.add_argument('-d', '--date',
                        help='Date of snapshot to parse. (Date format: DD-MM-YYYY)',
                        type=str,
                        required=True)
    parser.add_argument('-t', '--dataType',
                        help="The input data source.",
                        type=str,
                        choices=['rapid7', 'active'],
                        required=True)
    parser.add_argument('-i', '--inputFolder',
                        type=str,
                        help="The input folder path.",
                        required=True)

    args = parser.parse_args()

    resultPath = "results/" + args.dataType + "_" + args.date 
    createPath(resultPath)

    ccadb_hashes = load_ccadb_hashes()
    snapshot_timestamp  = datetime.datetime.strptime(args.date, '%d-%m-%Y').replace(tzinfo=timezone.utc).timestamp()

    if args.dataType == "active":
        files_l = load_active_scan_files(args.inputFolder)
        process_active_scan_data(files_l, ccadb_hashes, snapshot_timestamp, resultPath)

    elif args.dataType == "rapid7":
        process_rapid7_scan_data(args.inputFolder)

    else:
        pass

    
