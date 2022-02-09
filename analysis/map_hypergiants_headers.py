#!/usr/bin/python3
import sys
from fileinput import input
import radix # pip install py-radix or ppy-radix for pure python version
import io
import struct
import socket
import json

class HeaderMapper:

    def __init__(self):
        self.distinct_headers, self.exact_headers, self.value_substr, self.name_substr = get_header_filters()

    def map(self, header_name, header_value):
        
        header = '%s:%s' % (header_name, header_value)

        if header_name in self.distinct_headers:
            return self.distinct_headers[header_name]
        elif header in self.exact_headers:
            return self.exact_headers[header]

        for value_sub, value_net in self.value_substr.items():
            if header.startswith(value_sub):
                return value_net

        for name_sub,name_net in self.name_substr.items():
            if header_name.startswith(name_sub):
                return name_net

        return None


def load_asn_names(filename="../datasets/asn_names/asn-names.txt"):
    d = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                chunks = line.split()

                asn = chunks[0]
                name = ' '.join(chunks[1:])
                name = name.replace(',', ';')

                d[asn] = name
    except:
        print("Couldn't load/process TLD suffixes file \"{}\"".format(file_path_suffixes))
        return None
    return d


def isPublicASN(asn_int):
    # From RFC1930, RFC7607, RFC6793, RFC5398, RFC6996, RFC7300, RFC4893
    return asn_int != 0 and asn_int != 23456 and asn_int != 4294967295 and \
           not(64496 <= asn_int and asn_int <= 131071) and \
           not(4200000000 <= asn_int and asn_int <= 4294967294)


def isPublicIPv4Prefix(prefix):
    ip,_ = prefix.split('/')
    return isPublicIPv4Address(ip)


def isPublicIPv4Address(ip):
    return isPublicIPv4AddressInt(dottedQuadToNum(ip))


def isPublicIPv4AddressInt(asInt):
    return not(0 <= asInt and asInt < 16777216) and \
           not(167772160 <= asInt and asInt < 184549376) and \
           not(1681915904 <= asInt and asInt < 1686110208) and \
           not(2130706432 <= asInt and asInt < 2147483648) and \
           not(2851995648 <= asInt and asInt < 2852061184) and \
           not(2886729728 <= asInt and asInt < 2887778304) and \
           not(3221225472 <= asInt and asInt < 3221225728) and \
           not(3221225984 <= asInt and asInt < 3221226240) and \
           not(3232235520 <= asInt and asInt < 3232301056) and \
           not(3222405120 <= asInt and asInt < 3222536192) and \
           not(3325256704 <= asInt and asInt < 3325256960) and \
           not(3227017984 <= asInt and asInt < 3227018240) and \
           not(3405803776 <= asInt and asInt < 3405804032) and \
           not(3758096384 <= asInt)


def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('>L',socket.inet_aton(ip))[0]


def get_header_filters():
    distinct_headers = {}
    exact_headers = {}
    value_substr = {}
    name_substr = {}

    with open('configs/hypergiant-headers.txt', 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('#'):
                continue

            chunks = line.split(',')
            network = chunks[0]
            header_name = chunks[1].lower()
            header_name = header_name.replace('-', '_')

            header_value = chunks[2].lower()

            if header_name.endswith('*'):
                name_substr[header_name[:-1]] = network
            if not header_value: # if no header value
                distinct_headers[header_name] = network
            elif header_value.endswith('*'):
                nostar = header_value[:-1]
                tmp = header_name + ":" + nostar
                value_substr[tmp] = network
            else:
                tmp = header_name + ":" + header_value
                exact_headers[tmp] = network
    
    return distinct_headers, exact_headers, value_substr, name_substr


def main():
    asn_names = load_asn_names()
    if asn_names is None:
        exit()

    mapper = HeaderMapper()

    for line in input():

        line = line.strip()

        chunks = line.split('\t')

        if len(chunks) == 1:
            continue

        if len(chunks) != 2:
            sys.stderr.write('Error parsing line %s\n' % line)
            continue

        ip, headers_str = chunks

        network = None
        header_match = None

        headers = headers_str.split('|')


        for header in headers:
            header = header.lower()

            colon_index = header.find(':')
            if colon_index == -1:
                continue

            name = header[0:colon_index]
            value = header[colon_index+1:]

            network = mapper.map(name, value)
            if network:
                header_match = header
                break

        if network:
            print('%s\t%s\t%s' % (ip,network,header_match))

if __name__ == '__main__':
    main()
