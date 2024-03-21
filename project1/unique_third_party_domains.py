import argparse
import json
from urllib.parse import urlparse
from tld import get_fld
from tabulate import tabulate

def read_harfile(harfile_path, output_name):
    sourceFile = open(output_name, 'w')
    harfile = open(harfile_path)
    harfile_json = json.loads(harfile.read())
    i = 0
    for entry in harfile_json['log']['entries']:
        i = i + 1
        url = entry['request']['url']
        content_type = entry['response']['content']['mimeType'] 
        # scripts will have 'javascript' inside content type
        # images will have 'image' inside content type

        # Write url, content_type to output.txt
        print (url, content_type, file = sourceFile)
    sourceFile.close()
        
# Read in Macy's request data from harfile
read_harfile('www.macys.com.har', "macys.txt")

# Read in CNN's request data from harfile
read_harfile('www.cnn.com.har', "cnn.txt")

f = open('macys.txt', 'r')
macys_lines = f.readlines()

f = open('cnn.txt', 'r')
cnn_lines = f.readlines()

# Store list of fld for macys requests
aux_list = []
macys_list = []
for line in macys_lines:
    # Extract url from each line and get its first level domain name
    text = line.split()
    fld = get_fld(text[0])
    # Check if fld equals macys.com; if it does not, then the request is
    # third party
    if fld != 'macys.com':
        aux_list.append(fld)

# Add unique values to macys_list
for x in aux_list:
    if x not in macys_list:
        macys_list.append(x)

# Store list of fld for cnn requests
aux_list = []
cnn_list = []
for line in cnn_lines:
    # Extract url from each line and get its first level domain name
    text = line.split()
    fld = get_fld(text[0])
    # Check if fld equals macys.com; if it does not, then the request is
    # third party
    if fld != 'cnn.com':
        aux_list.append(fld)

# Add unique values to macys_list
for x in aux_list:
    if x not in cnn_list:
        cnn_list.append(x)

macys_length = len(macys_list)
cnn_length = len(cnn_list)

print("\n")
print(f"Number of unique third-party domains loaded when you visit...")
print(f"Cnn.com: {cnn_length}")
print(f"Macys.com: {macys_length}")
print("\n")

# Find the domains that exist in both macys_list and cnn_list
domains = []
for x in macys_list:
    if x in cnn_list:
        domains.append(x)

print(f"List of unique third-party domains that appear on both macys.com and cnn.com: ")
for domain in domains:
    print(domain)
print("\n")

# Store list of filterURLS
filterURLS = []

f = open('disconnect.json')

# Load json file
json = json.load(f)

# list of categories:
categories = ['Email', 'EmailAggressive', 'Advertising', 'Content', 'Analytics', 'FingerprintingInvasive', 'FingerprintingGeneral', 'Social', 'Cryptomining', 'Disconnect']

for category in categories:
    numDomains = len(json['categories'][category])
    for i in range(0, numDomains):
        domain = json['categories'][category][i];
        for v in domain.values():
            for x in v.values():
                filterURLS.append(x[0])

# Clean filterURLS list of unneccesary values (items of length 1)
for url in filterURLS:
    length = len(url)
    if length == 1:
        filterURLS.remove(url)

# Compare filterURLS list with each request URL while visiting cnn.com and macys.com

# Macys
# number of macys requests denied 
macys_requests_blocked = 0
cnn_requests_blocked = 0
for url in filterURLS:
    for request in macys_list:
        if url == request:
            macys_requests_blocked = macys_requests_blocked + 1
    for request in cnn_list:
        if url == request:
            cnn_requests_blocked += 1

requests_blocked = [['Cnn.com', cnn_requests_blocked], ["Macy's.com", macys_requests_blocked]]

print(tabulate(requests_blocked, headers = ['Website', '# of requests blocked']))

print("\n")







