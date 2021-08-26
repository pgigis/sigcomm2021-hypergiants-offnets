#!/usr/bin/python3
from base64 import b64decode
from fileinput import input
from json import loads
import sys

ignore_header_list = ["Date", "Cache-Control", "Content-Length", "Content-Type", "Expires", "Connection", "Transfer-Encoding", "X-AspNet-Version",
                      "Mime-Version", "Accept-Ranges", "ETag", "Last-Modified", "Pragma", "X-Content-Type-Options", "Content-Encoding",
                      "Status", "WWW-Authenticate", "Referrer-Policy", "Content-Language", "X-Frame-Options", "Keep-Alive", "Retry-After",
                      "Access-Control-Allow-Headers", "Access-Control-Allow-Methods", "Access-Control-Allow-Credentials", "Age",
                      "X-XSS-Protection", "Strict-Transport-Security", "Proxy-Authenticate", "P3P", "Content-Security-Policy", "Authentication"
                      "Access-Control-Allow-Origin: *", "Vary: Accept-Encoding", "X-Powered-By: ASP.NET", "X-Squid-Error: ERR_INVALID_URL 0", "X-Redirect-By: WordPress", "X-Powered-By: Nginx",                         "Vary: User-Agent,Accept-Encoding", "X-UA-Compatible: IE=Edge", "Timing-Allow-Origin: *", "Server:Microsoft-HTTPAPI/2.0", "X-UA-Compatible:IE=EmulateIE7", "Vary: Accept-Encoding,User-Agent",
                      "X-Permitted-Cross-Domain-Policies: none", "Location: /404.html", "Vary: Cookie,Accept-Encoding", "Location: /weblogin.htm", "X-Proxy-Cache: MISS", "X-Squid-Error: ERR_ACCESS_DENIED 0",
                      "location: error.php"]

ignore_header_prefixes = ("Server: Microsoft-IIS", "X-Powered-By: PHP", "Server: nginx", "Server: Apache", "Server: squid", "Server: lighttpd", "Server: Microsoft-HTTPAPI")


def main():
    ignore = set([i.lower() for i in ignore_header_list])

    for line in input():
        try:
            json_str = line.strip()
            json_obj = loads(json_str)

            base64_response = json_obj['data']
            ip = json_obj['ip']

            if not ip or '.' not in ip:
                continue

            response_str = b64decode(base64_response).decode('iso-8859-1')

            start_of_html = response_str.find('\r\n\r\n')

            if start_of_html == -1:
                continue

            headers_str = response_str[0:start_of_html]

            headers = headers_str.split('\r\n')
            header_list = []
            for i in range(1, len(headers)):
                header = headers[i]

                colon_index = header.find(':')
                if colon_index == -1:
                    continue

                header_name = header[0:colon_index]
                header_value = header[colon_index+1:]

                header_name = header_name.strip()
                header_value = header_value.strip()

                if header_name and header_value and header_name not in ignore and header_name.lower() not in ignore and header.lower() not in ignore and not header.startswith(ignore_header_prefixes):
                    header_value = ' '.join(header_value.split())  # get rid of any whitespace
                    header_list.append("%s:%s" % (header_name, header_value))

            header_out = '|'.join(header_list)
            print("%s\t%s" % (ip, header_out))

        except:
            sys.stderr.write('Error parsing line %s\n' % line)


main()