#!/usr/bin/env python3

import argparse
import json
import os
import random
import re
import requests
import time
import sys
from pprint import pprint as pp

BASE_URL = "https://us.api.insight.rapid7.com/opendata/"
SLEEP_TIME_BETWEEN_OPS = 10 # seconds

def get_quotas(api_keys):
    quota_info = {}
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Api-Key": None
    }
    for api_key in api_keys:
        headers["X-Api-Key"] = api_key
        quota_info[api_key] = requests.get(url=BASE_URL + "quota/", headers=headers).json()
    return quota_info

def clean_filename(filename):
    return filename.split('/')[-1]

parser = argparse.ArgumentParser(description="""
download sonar data using API (rapid7)
""")
parser.add_argument('-k', "--keys", dest="api_keys_file", type=str, help="file with API keys", default="api_keys.txt")
parser.add_argument('-o', "--out_dir", dest="out_dir", type=str, help="output directory with downloaded files", default='.')
args = parser.parse_args()

assert os.path.isfile(args.api_keys_file)
out_dir = args.out_dir.rstrip('/')
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

api_keys = set()
with open(args.api_keys_file, 'r') as f:
    for line in f:
        api_keys.add(line.rstrip('\n'))
api_keys = list(api_keys)

# select randomly an API key to check what files to download
check_api_key = random.choice(list(api_keys))
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Api-Key": check_api_key
}
"""
# retrieve the filenames and information of all needed files
print("Fetching newest sonar.ssl study info...", end='\r')
new_sonar_ssl_study_info = requests.get(url=BASE_URL + "studies/sonar.moressl/", headers=headers).json()
print("Fetching sonar.moressl study info...done")
print("Checking if update is required for sonar.moressl study info...", end='\r')

study_info_file = "{}/study_info.json".format(out_dir)

with open(study_info_file, 'wt') as f:
    f.write("{}\n".format(json.dumps(new_sonar_ssl_study_info)))
"""

study_info_file = "{}/study_info.json".format(out_dir)


download_files_to_skip = dict()

files_to_skip = ['../../datasets/tls_scans/rapid7/certificates/more_ssl_certificates_non_443_filenames.txt',
                '../../datasets/tls_scans/rapid7/certificates/ssl_certificates_https_443_filenames.txt',
                '../../datasets/tls_scans/rapid7/certificates/ssl_certificates_https_non_443_filenames.txt'
                ]

for file in files_to_skip:
    with open(file, 'rt') as f:
        for line in f:
            download_files_to_skip[line.rstrip()] = None

with open(study_info_file, 'rt') as f:
    sonar_ssl_study_info = json.load(f)


all_sonar_ssl_files = sonar_ssl_study_info["sonarfile_set"]
needed_sonar_ssl_files = set()
for filename in all_sonar_ssl_files:
    name = filename
    if '/' in filename:
        name = filename.split("/")[1]
    if 'certs' in name:
        if name not in download_files_to_skip:
            print(filename)

exit()

sonar_ssl_files_info_file = "{}/file_info.json".format(out_dir)
sonar_ssl_files_info = {}
if os.path.isfile(sonar_ssl_files_info_file):
    with open(sonar_ssl_files_info_file, 'r') as f:
        sonar_ssl_files_info = json.load(f)
missing_sonar_ssl_files = set(needed_sonar_ssl_files) - set(sonar_ssl_files_info.keys())
for i,filename in enumerate(list(missing_sonar_ssl_files)):
    print("Fetching missing file info...{}/{}".format(i+1, len(missing_sonar_ssl_files)), end='\r')
    sonar_ssl_files_info[filename] = requests.get(url=BASE_URL + "studies/sonar.ssl/{}/".format(filename), headers=headers).json()
with open("{}/file_info.json".format(out_dir), 'w') as f:
    json.dump(sonar_ssl_files_info, f)
print("Fetching missing file info...{}/{} (done)".format(len(missing_sonar_ssl_files), len(missing_sonar_ssl_files)))
"""
#
# quota_allowed tells you how many download URL requests you can perform per quota_timespan seconds
# quota_used describes how many download URLs you requested in the last quota_timespan seconds
# quota_left describes how many download URLs you can still request until you exhausted your quota.
# oldest_action_expires_in describes how long it takes until the oldest URL you requested is quota_timespan seconds old. When this happens you receive one more download to perform. NOTE:If you didn't request any URLs in the last quota_timespan seconds, this field is not present.
#
"""

quota_info = {}
quota_info_file = "{}/quota_info.json".format(out_dir)
downloaded_files = set()
missing_sonar_ssl_file_data = set()
for filename in sonar_ssl_files_info:
    full_path = "{}/{}".format(out_dir, clean_filename(filename))
    if not os.path.isfile(full_path):
        if not ("detail" in sonar_ssl_files_info[filename] and sonar_ssl_files_info[filename]["detail"] == "Not found."):
            missing_sonar_ssl_file_data.add(filename)



downloaded_files = set()
missing_sonar_ssl_file_data = set()
with open('files_to_get.txt', 'rt') as f:
    for line in f:
        missing_sonar_ssl_file_data.add(line.rstrip())

files_got = dict()
with open('files_got.txt', 'rt') as f:
    for line in f:
        files_got[line.rstrip()] = None

to_remove = list()
for file in missing_sonar_ssl_file_data:
    if file.split('/')[1] in files_got:
        to_remove.append(file)

for rem in to_remove:
    missing_sonar_ssl_file_data.remove(rem)


print("Downloading missing files ...{}/{}".format(len(downloaded_files), len(missing_sonar_ssl_file_data)), end='\r')
missing_sonar_ssl_file_data = list(missing_sonar_ssl_file_data)
next_file_index_to_download = 0
while len(downloaded_files) < len(missing_sonar_ssl_file_data):
    next_file_to_download = missing_sonar_ssl_file_data[next_file_index_to_download % len(missing_sonar_ssl_file_data)]

    #assert not ("detail" in sonar_ssl_files_info[next_file_to_download] and sonar_ssl_files_info[next_file_to_download]["detail"] == "Not found.")
    print("Downloading missing files ...{}/{}\t\t\t\t\t\t\t".format(len(downloaded_files), len(missing_sonar_ssl_file_data)), end='\r')

    quota_info = get_quotas(api_keys)
    #with open(quota_info_file, 'w') as f:
    #    json.dump(quota_info, f)
    download_url = None
    selected_api_key = None
    random.shuffle(api_keys)
    for api_key in api_keys:
        if 'quota_left' in quota_info[api_key] and quota_info[api_key]["quota_left"] > 0:
            selected_api_key = api_key
            break
    if selected_api_key:
        headers["X-Api-Key"] = selected_api_key
        download_url_req = requests.get(url=BASE_URL + "studies/sonar.ssl/{}/download/".format(next_file_to_download), headers=headers)
        if download_url_req.status_code == 200:
            download_url_json = download_url_req.json()
            #sonar_ssl_files_info[next_file_to_download]["download_url"] = download_url_json["url"]
            download_url = download_url_json["url"]
            #with open("{}/file_info.json".format(out_dir), 'w') as f:
            #   json.dump(sonar_ssl_files_info, f)
        else:
            print("error on {}".format(next_file_to_download))
            #missing_sonar_ssl_file_data.remove(next_file_to_download)
    else:
        wait_time = 1000000000
        for api_key in api_keys:
            if 'oldest_action_expires_in' not in quota_info[api_key]:
                continue
            wait_time = min(wait_time, quota_info[api_key]["oldest_action_expires_in"])
        slept = 0
        while slept < wait_time:
            print("Downloading missing files ...{}/{} (sleeping for {} seconds)".format(
                len(downloaded_files),
                len(missing_sonar_ssl_file_data),
                wait_time-slept), end='\r')
            time.sleep(SLEEP_TIME_BETWEEN_OPS)
            slept += SLEEP_TIME_BETWEEN_OPS
    if download_url:
        with open("{}/{}".format(out_dir, clean_filename(next_file_to_download)), 'wb') as f:
            r = requests.get(download_url, stream=True)
            total_length = r.headers.get('content-length')
            dl = 0
            total_length = int(total_length)
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = "unknown"
                if total_length:
                    done = round(100.0*dl/total_length, 2)
                print("Downloading missing files ...{}/{} (current file: {}%)\t\t\t\t\t\t\t".format(
                    len(downloaded_files),
                    len(missing_sonar_ssl_file_data),
                    done
                ), end='\r')
        next_file_index_to_download += 1
        downloaded_files.add(next_file_to_download)
    quota_info = get_quotas(api_keys)
    #with open(quota_info_file, 'w') as f:
    #    json.dump(quota_info, f)
    time.sleep(SLEEP_TIME_BETWEEN_OPS)
quota_info = get_quotas(api_keys)
#with open(quota_info_file, 'w') as f:
#    json.dump(quota_info, f)
time.sleep(SLEEP_TIME_BETWEEN_OPS)
print("Downloading missing files ...{}/{} (done)\t\t\t\t\t\t\t".format(len(missing_sonar_ssl_file_data), len(missing_sonar_ssl_file_data)))