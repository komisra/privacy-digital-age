import argparse
import json
from adblockparser import AdblockRules
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
        
# Read in CNN's request data from harfile
read_harfile('www.cnn.com.har', "cnn.txt")

f = open('cnn.txt', 'r')
cnn_lines = f.readlines()

# Store number of requests blocked for each rule
a_requests_blocked = 0
b_requests_blocked = 0
c_requests_blocked = 0

raw_rules = ["/cookiesync?"]

rules = AdblockRules(raw_rules)

for line in cnn_lines:
    #3a
    if rules.should_block(line.split()[0]):
        a_requests_blocked += 1

raw_rules = ["scorecardresearch.com/img"]

rules = AdblockRules(raw_rules)

for line in cnn_lines:
    #3b
    if rules.should_block(line.split()[0], {'image': True} ):
        b_requests_blocked += 1
    if "scorecardresearch.com" in line:
        if "image" in line:
            b_requests_blocked += 1

raw_rules = ["doubleclick.net^$script"]

rules = AdblockRules(raw_rules)

for line in cnn_lines:
    #3c
    if rules.should_block(line.split()[0], {'script': True} ):
        c_requests_blocked += 1


requests_blocked = [["Block any request containing ‘cookiesync?'", a_requests_blocked], ["Block any image (e.g., jpg, gif etc.) loading from scorecardresearch.com", b_requests_blocked], ["Block any script loading from doubleclick.net", c_requests_blocked]]

print(tabulate(requests_blocked, headers = ['Rule', '# of HTTP requests blocked']))





