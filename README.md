# _"Seven Years in the Life of Hypergiants' Off-Nets"_

Table of Contents
* [Project Website](#project-website)
* [Getting Started](#getting-started)
    * [Prerequisites and Installation](#prerequisites-and-installation)
    * [Getting Acccess to the Datasets](#getting-acccess-to-the-datasets)
* [Results Overview](#results-overview)
* [Analysis](#analysis)
* [Meta-Analysis](#meta-analysis)

## Project Website 
Explore our findings through our project website:
https://pgigis.github.io/hypergiants-offnets/

## Getting Started
### Prerequisites and Installation
The entire software was written in python3, which has to be pre-installed on your system.

Install pip3:
```
sudo apt-get install python3-pip
```

In order to isolate the following installation and runs from other parts of the system, we can run everything in a python3 venv environment. This can be done according to the instructions on the
[python3 venv tutorial](https://docs.python.org/3/tutorial/venv.html).

Please, follow the aforementioned guide to set up an environment on your system.

Then, install the required python3 packages within the venv:
```
pip3 install -r requirements.txt
```
In case a required dependency is missing, please contact [p.gkigkis at cs.ucl.ac.uk]().


### Getting Acccess to the Datasets
Our methodology uses TLS certificate scans as a building block, supplementing them with additional techniques (e.g., HTTP(S) fingerprints) and datasets (e.g., IP-to-AS mapping, APNIC user population estimates, etc..). 

We document in detail the datasets [here](https://github.com/pgigis/sigcomm2021-hypergiants-offnets/tree/master/datasets).



## Results Overview

The [Analysis](#analysis) step allows you to infer the off-nets per hypergiant by reproducing the methodology section of the paper.

Then, to explore the results we provide additional [Meta-Analysis](#meta-analysis) scripts. 

Meta-Analysis ```Group Hypergiant validated off-nets by continent``` allows you to reproduce the results used in Figure 5.

Meta-Analysis ```Estimate Hypergiant country coverage``` allows you to reproduce the Internet user population coverage (percentage) per country for off-net footprints results used in Figures 6, 7 and 8.


## Analysis
For the analysis part, we suggest to populate the ```datasets``` folder of this repository, following these [instructions](https://github.com/pgigis/sigcomm2021-hypergiants-offnets/tree/readme/datasets).
The next steps suffice to infer the off-nets of the considered Hypergiants in this study. We will include more analysis commands that are available in the software at a later stage.


### **Step 0**:
```
cd analysis
```

### **Step 1**: Extract End-Entity (EE) certificates.

As a first step, the script takes as an input the certificate dataset and extracts the End-Entity (EE) certificate of each IP.
Expired, self-signed and root/intermediate certificates that are not present in the CCADB [Common CA Database](https://www.ccadb.org) are filtered out.

Currently, as an input we support the following two datasets:

1) Active Scan (Certigo) - *Suggested*
2) Rapid7 TLS scans 

To run the script, execute the following command:
```
python3 extract_valid_certs.py -d 21-11-2019 -t active -i ../datasets/tls_scans/active/
```

This will generate the folder ```active_21-11-2019``` inside the ```analysis/results```.
Inside the folder it will create a single JSON line-by-line file ```"ee_certs.txt"```. Each line contains a JSON object formatted as:
```
{ "ip" : "EndEntity-Certificate" }
```


### **Step 2**: Find TLS fingerprints using hypergiant on-net certificates.
Script ```extract_hypergiant_on-net_certs.py``` takes as an input the generated file of step 1, the configuration file, the list of HG ASes and, the IP-to-AS mapping.

The configuration file contains a mapping between the candidate HG keyword and the HG ASes.
Here is an example of a configuration file. 
```
{"hypergiant-keyword" : "google", "hypergiant-ases-key" : "google"}
{"hypergiant-keyword" : "facebook", "hypergiant-ases-key" : "facebook"}
{"hypergiant-keyword" : "netflix", "hypergiant-ases-key" : "netflix"}
{"hypergiant-keyword" : "akamai", "hypergiant-ases-key" : "akamai"}
{"hypergiant-keyword" : "alibaba", "hypergiant-ases-key" : "alibaba"}
```

Any value can be used as a ```"hypergiant-keyword"```. For the ```"hypergiant-ases-key"``` we support the following values:
```
['yahoo', 'cdnetworks', 'limelight', 'microsoft', 'chinacache', 'apple', 'alibaba', 'amazon', 'akamai', 'bitgravity', 'cachefly', 'cloudflare', 'disney', 'facebook', 'google', 'highwinds', 'hulu', 'incapsula', 'netflix', 'cdn77', 'twitter', 'fastly']
```

To run the script, execute the following command:
```
python3 extract_hypergiant_on-net_certs.py -s ../datasets/hypergiants/2019_11_hypergiants_asns.json  -i results/active_21-11-2019/ee_certs.txt  -c configs/config.txt -a ../datasets/ip_to_as/2019_11_25thres_db.json
```

This will create a folder ```"on-nets"``` inside ```"analysis/results/active_21-11-2019/"```. The folder contains a file per HG keyword. Each file includes only the ```dns_names``` and ```subject:organization``` fields of the EE certificates found in IP addresses of the HG AS(es) using this specific keyword. 

Here is an output example. 
```
{"ip": "23.72.3.228", "ASN": 16625, "dns_names": ["try.akamai.com", "threatresearch.akamai.com"], "subject:organization": "akamai technologies, inc. "}
{"ip": "23.223.192.18", "ASN": 20940, "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. "}
{"ip": "172.232.1.72", "ASN": 20940, "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. "}
{"ip": "210.61.248.97", "ASN": 20940, "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. "}
```


### **Step 3**: Find candidate hypergiant off-nets. 
Script ```extract_hypergiant_off-net_certs.py``` takes as an input the generated file of step 1, the generated folder of step 2, the list of HG ASes and, the IP-to-AS mapping.

To run the script, execute the following command:
```
python3 extract_hypergiant_off-net_certs.py -s ../datasets/hypergiants/2019_11_hypergiants_asns.json -i results/active_21-11-2019/ee_certs.txt -c configs/config.txt -a ../datasets/ip_to_as/2019_11_25thres_db.json -o results/active_21-11-2019/on-nets
```

This will create a folder ```"candidate_off-nets"``` inside ```"analysis/results/active_21-11-2019/"```. The folder contains a file per HG keyword. Each file includes only the ```dns_names``` and ```subject:organization``` fields of the EE certificates found in IP addresses outside of the HG AS(es) using this specific keyword. 

Here is an output example. 
```
{"ip": "80.239.236.44", "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. ", "ASN": 1299}
{"ip": "2.18.52.28", "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. ", "ASN": 33905}
{"ip": "2.16.173.163", "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. ", "ASN": 20940}
{"ip": "77.94.66.28", "dns_names": ["a248.e.akamai.net", "*.akamaized-staging.net", "*.akamaized.net", "*.akamaihd-staging.net", "*.akamaihd.net"], "subject:organization": "akamai technologies, inc. ", "ASN": 60772}
```


### **Step 4**: Parse HTTP and HTTPS headers.
Please, refer [here](https://github.com/pgigis/sigcomm2021-hypergiants-offnets/tree/master/datasets#how-to-download-a-file-from-rapid7-open-data-platform) on how to obtain the HTTP(S) header files. Due to the size of these files (~60GB compressed), we suggest to not completely uncompress them.
In our analysis, we always use the ```gunzip -kc``` flags to keep the files compressed, while sending the output to stdout.

**Step 4.1** Find the HTTP(S) header names.

Execute the following command:
```
gunzip -kc ../datasets/headers/http/2019-11-18-1574121404-http_get_80.json.gz | ./parse_rapid7_headers.py | awk -F'\t' '{ if(NF == 2) print $0 }' | gzip > results/active_21-11-2019/header_names_2019-11-18-1574121404-http_get_80.json.gz
```

The output of the script is a tab separated line with ```<ip>\t<header-list>```. Each header name and header value pair is separated by ":", and each header pair is separated by "|". The script contains a list of "uninteresting" headers which are ignored (e.g., "Server: Apache/PHP"). Finally, IP values without "interesting" headers or any headers at all, are output with an empty ```header-list```, so we can keep track of IP addresses missing from the dataset.

Here is an output example. 
```
104.24.40.135   Set-Cookie:__cfduid=d388387dd3c34cc6c4e37c62d3bc4beb91574121663; expires=Wed, 18-Nov-20 00:01:03 GMT; path=/; domain=.104.24.40.135; HttpOnly|Server:cloudflare|CF-RAY:537de84e0b49ed37-SJC
23.231.139.150
45.38.39.238
167.82.1.144    Server:Varnish|X-Served-By:cache-bur17520-BUR|Via:1.1 varnish
107.165.5.254   Upgrade:h2
104.25.187.85   Set-Cookie:__cfduid=d51c717c0d086ff466c032113ed7265601574121664; expires=Wed, 18-Nov-20 00:01:04 GMT; path=/; domain=.104.25.187.85; HttpOnly|Server:cloudflare|CF-RAY:537de8506816ed2f-SJC
23.57.49.186    Server:AkamaiGHost
```

**Step 4.2** Apply the header rules in hypergiant-headers.txt to the file generated in step 4.1.

The ```map_networks.py``` script outputs a tab separated line of ```ip, hypergiant, header_match```. IPs with no CDN header matches are also output to keep track of what IPs exist in the data.

Execute the following command:
```
gunzip -kc results/active_21-11-2019/header_names_2019-11-18-1574121404-http_get_80.json.gz | python3 ./map_hypergiants_headers.py | gzip > results/active_21-11-2019/mapped_header_names_headers_names_2019-11-18-1574121404-http_get_80.json.gz
```

Here is an output example. 
```
104.24.40.135   Cloudflare      server:cloudflare
104.25.187.85   Cloudflare      server:cloudflare
23.57.49.186    Akamai  server:akamaighost
104.18.84.77    Cloudflare      server:cloudflare
104.144.176.112 Alibaba server:tengine/2.0.0
52.7.82.238     Amazon  server:awselb/2.0
```

Note: For each snapshot you need to download only the corresponding HTTP and HTTPs header files with the alligned dates from Rapid7.


### **Step 5**: Compare candidate off-nets with HTTP(S) fingerprints.
The ```find_offnets.py``` script takes as an input the candidate off-nets folder of Step 3, and the HTTP(S) header fingerprints of Step 4.

Execute the following command:
```
python3 find_offnets.py -o results/active_21-11-2019/candidate_off-nets/ -https results/active_21-11-2019/mapped_headers_names_https_2019-11-18-1574084778-https_get_443.json.gz -http results/active_21-11-2019/mapped_headers_names_2019-11-18-1574121404-http_get_80.json.gz
```

This will generate the folder ```"candidate-off-nets"``` inside the ```"analysis/results"```. The folder contains a file per HG with the off-net ASes and their corresponding IP addresses.

Here is the JSON format of each file:
```
{ "AS-1" : [ "IP-1", "IP-2" ],  "AS-2" : [ "IP-3", "IP-4", "IP-5", "IP-6" ] }
```


## Meta-Analysis

### **Exploring results**

The ```explore_results.py``` script outputs the inferred off-nets per hypergiant at AS-level granularity. The script takes as input the result folder of the analysis part.

Execute the following command:
```
python3 explore_results.py  -i ../analysis/results/active_21-11-2019/
```

Here is an output example. 
```
HG Keyword: 'akamai'
Found Candidate Off-nets (only certificates) in 1228 ASes.
Found Off-nets (validated with HTTP(s) headers) in 1187 ASes.
-------------------------------------------------------------------

HG Keyword: 'disney'
Found Candidate Off-nets (only certificates) in 194 ASes.
Found Off-nets (validated with HTTP(s) headers) in 0 ASes.
-------------------------------------------------------------------
```

You can also get a list of the ASes per hypergiant, using the argument ```-p true```, by executing the following command:
```
python3 explore_results.py  -i ../analysis/results/active_21-11-2019/ -p true
```

Here is an output example. 
```
HG Keyword: 'alibaba'
Found Candidate Off-nets (only certificates) in 300 ASes.
Found Off-nets (validated with HTTP(s) headers) in 154 ASes.
ASes for Candidate Off-nets:
AS136192, AS136193, AS4609, AS136195, AS6147, AS20485, AS45061, ...
- - -
ASes for Validated Off-nets:
AS577, AS17897, AS136188, AS9394, AS54994, AS131565, AS58519, AS134771, ...
-------------------------------------------------------------------

HG Keyword: 'disney'
Found Candidate Off-nets (only certificates) in 194 ASes.
Found Off-nets (validated with HTTP(s) headers) in 0 ASes.
ASes for Candidate Off-nets:
AS4609, AS6147, AS8708, AS55818, AS13335, AS15897, AS19994, ...
- - -
ASes for Validated Off-nets:
-------------------------------------------------------------------
```

### **Group Hypergiant validated off-nets by continent**
The ```group_by_continent.py``` script takes as input the result folder of the analysis part (uses the validated off-nets) and the CAIDA AS-to-Organization info dataset. To obtain the latter dataset refer [here](https://github.com/pgigis/sigcomm2021-hypergiants-offnets/tree/master/datasets).


Execute the following command:
```
python3 group_by_continent.py -i ../analysis/results/active_21-11-2019 -c ../datasets/organization_info/20191101.as-org2info.txt
```

The script creates ```results/active_21-11-2019/offnets_to_continents``` inside the meta-analysis folder. For each hypergiant it creates a text file formatted as follows:

Here is an output example for ```google```.
```
EU: 793 ASes
AF: 166 ASes
SA: 874 ASes
AS: 778 ASes
NA: 403 ASes
OC: 51 ASes
# # #
EU: AS34058, AS41794, AS5550, AS34187, AS8218, ...
- - - 
AF: AS10474, AS36992, AS24835, AS327818, AS37612, ...
- - - 
SA: AS266445, AS23140, AS262676, AS262634, AS263244, ...
- - - 
AS: AS133830, AS135772, AS15802, AS132735, AS45271, ...
- - - 
NA: AS26133, AS600, AS53435, AS36728, AS19165, ... 
- - - 
OC: AS132797, AS18200, AS10131, AS9790, AS133612, ... 
- - - 
```


### **Estimate Hypergiant country coverage**
The ```country_coverage.py``` script takes as input the result folder of the analysis part (uses the validated off-nets) and the APNIC user population per ASN estimates.

Execute the following command:
```
python3 country_coverage.py -i ../analysis/results/active_21-11-2019 -a ../datasets/apnic_population_estimates/2019_11.json
```

The script creates ```results/active_21-11-2019/country_coverage``` inside the meta-analysis folder. For each hypergiant it creates a text file formatted as follows:

```
Country-Alpha‑2-code,Coverage-Percentage 
```

Here is an output example.
```
BD,82.89108306883769
BE,54.36254335595898
BF,86.31532375598584
BG,62.11203725552794
BA,80.72960244254675
BB,98.43826732090602
```