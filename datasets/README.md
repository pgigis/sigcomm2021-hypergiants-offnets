# Datasets

## Historical Datasets
Due to the size of the datasets, we provide [here](https://liveuclac-my.sharepoint.com/:f:/g/personal/ucabpgk_ucl_ac_uk/Eim32GoBUgVOoLolQCYbbyMBSf-PiNBbOzuQl52n3Xm94w?e=7GOz5l) an OneDrive directory, that contains additional datasets used in this work. Access password is: ```sigcomm2021-476```

For our longitudinal analysis, we used TLS certificate scans and HTTP(S) headers, derived from the [Rapid7 - Open Data](https://opendata.rapid7.com) platform.

To access the historical datasets of Rapid7 Open Data platform you need to apply for an account.
```Data access is free to Practitioners, Academics, and Researchers.```

To create an account on the Rapid7 Opendata platform visit:
https://opendata.rapid7.com/sonar.ssl/

Then, search "Gain Unlimited Access to Our Datasets" (located close to the bottom of the page) and click on "Create a free account".
To fully reproduce our findings, you will need to gain access to the following datasets.
* SSL Certificates
* More SSL Certificates (non-443)
* HTTP GET Responses
* HTTPS GET Responses

### How to download a file from Rapid7 Open Data platform
At first, you need to create an account and create an API key.

After this, by using the following command, you can request a download link from Rapid7. (Note: The link is only valid for a few hours.)
```
curl -H "X-Api-Key: XXX" https://us.api.insight.rapid7.com/opendata/studies/<DATASET-NAME>/<FILENAME>/download/
```
To successfully execute the above command, you will need an API key, the dataset name (e.g., sonar.http or sonar.https) and the download file name (e.g., 2019-11-18-1574121404-http_get_80.json.gz).

Then, you can receive a download link and by using the example below, you can resume the download, if it is interrupted, and will work even if you use a new URL.
```
curl -L -o 2019-11-18-1574121404-http_get_80.json.gz -C - https://f002.backblazeb2.com/file/rapid7-opendata/sonar.http/2019-11-18-1574121404-http_get_80.json.gz?Authorization=30023402023
```

The official Rapid7 Open Data API documentation is [here](https://opendata.rapid7.com/apihelp/).


## TLS/SSL scans
In this work, we used three different sources of TLS/SSL scans (Rapid7 - Open Data, Censys, Active Scan).

### Rapid7 
The TLS/SSL scans that we used in our longitudinal analysis can be found [here](https://opendata.rapid7.com/sonar.ssl/). In our study, we used the HTTPS GET requests on port-443. More specifically, in our analysis we use the ```_hosts``` and ```_certs``` files.

According to the Rapid7 dataset [documentation](https://opendata.rapid7.com/sonar.ssl/):

> The ```_hosts``` files provide mapping between the IPs/endpoints and the fingerprint of the X.509 certificate presented.
> The ```_certs``` file provides a mapping of the net new certificates from a given study and the corresponding fingerprint. 

In our analysis, we had to download all ```_certs``` available to construct a global mapping between fingerprints and the raw certificates in PEM format.
Moreover, we found that some fingerprints were not present in the related to HTTPS GET port-443 files, and consequently we downloaded all ```_certs``` of both available TLS/SSL certificate datasets ([SSL Certificates](https://opendata.rapid7.com/sonar.ssl/) and [More SSL Certificates (non-443)](https://opendata.rapid7.com/sonar.moressl/)). We list exactly which files we used, in order to construct the mapping between fingerprints and raw certificates [here-1](https://github.com/pgigis/sigcomm2021-offnets-artifacts/blob/master/datasets/tls_scans/rapid7/certificates/ssl_certificates_https_443_filenames.txt), [here-2](https://github.com/pgigis/sigcomm2021-offnets-artifacts/blob/master/datasets/tls_scans/rapid7/certificates/more_ssl_certificates_non_443_filenames.txt) and [here-3](https://github.com/pgigis/sigcomm2021-offnets-artifacts/blob/master/datasets/tls_scans/rapid7/certificates/ssl_certificates_https_non_443_filenames.txt). 

How to proccess Rapid7 scans:

After you obtain all ```_certs``` files, you have to create a mapping file between fingerprints/hashes and the raw PEM certificates.

The desired file should be formatted as follows:
```
Fingerprint-1, Raw-PEM-1
Fingerprint-2, Raw-PEM-2
Fingerprint-3, Raw-PEM-3
```

Then, you will need to transform the raw PEM certificate entries to JSON formatted entries. To do this efficiently, we modified the Certigo tool to take as input a file formatted as previously described.

You can find our custom Certigo version [here](https://github.com/pgigis/certigo).

To run the tool, execute the following command:
```
./certigo dump -j -f PEM -w ../pems.txt > translated.txt
```

This will generate a file in the following format:
```
Fingerprint-1, JSON-CERTIFICATE-1
Fingerprint-2, JSON-CERTIFICATE-1
Fingerprint-3, JSON-CERTIFICATE-1
```

Using this file, you can process the hosts files and map an IP address with to the corresponding JSON formatted certificate.



### Censys
We applied for a research account to the [Censys](https://censys.io/) platflorm and used the Google's BigQuery platform to retrieve TLS/SSL scans. You can read more on how to obtain Research access to the Censys platform [here](https://support.censys.io/hc/en-us/articles/360038761891-Research-Access-to-Censys-Data).

Here is an query example that was used to retrieve TLS data:
```
select c.ip, d.parsed.names, d.parsed.subject_dn 
from `censys-io.ipv4_public.20191119` c inner join `censys-io.certificates_public.certificates` d  on d.parsed.fingerprint_sha256 = c.p443.https.tls.certificate.parsed.fingerprint_sha256
```

### Active Scan (Certigo)
Except from the passive TLS scanning datasets, we also conducted in Nov. 2019 an active scan using the [Certigo](https://github.com/square/certigo) tool.

The active scan dataset can be found [here](https://liveuclac-my.sharepoint.com/:f:/g/personal/ucabpgk_ucl_ac_uk/Ekb_VbFdQghCntUHh98v-NoBdnSdS_XAh6859ME1RCLDpQ?e=jFeGnZ). Access password is: ```sigcomm2021-476```

Please, copy the contents of the OneDrive folder in the ```tls_scans/active``` folder.

### HTTP headers
The HTTP GET Responses that we used in our analysis can be found [here](https://github.com/pgigis/sigcomm2021-offnets-artifacts/blob/master/datasets/headers/http/http_80_filenames.txt).

### HTTPS headers
The HTTPS GET Responses that we used in our analysis can be found [here](https://github.com/pgigis/sigcomm2021-offnets-artifacts/blob/master/datasets/headers/https/https_443_filenames.txt).


## IP-to-AS Mapping
The IP-to-AS mappings that we used in this work can be found [here](https://liveuclac-my.sharepoint.com/:f:/g/personal/ucabpgk_ucl_ac_uk/EujvVAp0lqBBpY-EgY5IZSgBLTgoxv7xwtRW92YGe9hDLA?e=2iSwLV). Access password is: ```sigcomm2021-476```

Please, copy the contents of the OneDrive folder in the ```ip_to_as``` folder.


## User population per ASN data
APNIC conducts measurement campaigns and publishes the related results on a daily basis. We download daily snapshots and we keep only the ASes that have been present in the dataset for at least 25% of each month (one week) to avoid misinferences. The snapshots that we used can be found in the ```apnic_population_estimates``` folder.


## Hypergiant ASes
The hypergiant ASes across time can be found in ```hypergiants``` folder.


## AS-to-Organization info
This dataset is provided by [CAIDA](https://www.caida.org).
You can download the datasets [here](https://publicdata.caida.org/datasets/as-organizations/).

You need to download only files ending with ".as-org2info.txt.gz".


