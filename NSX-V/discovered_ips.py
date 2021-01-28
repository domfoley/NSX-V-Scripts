####  A Python script to check the discovered IP's on a filter for all hosts in an NSX-V Environment ### 

import sys
sys.path.append('.')

import ssl
import json
import requests
import urllib3
import xmltodict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ssl._create_default_https_context = ssl._create_unverified_context
s = requests.Session()
s.verify = False

# Enter NSX-V Manager Username / Password
s.auth = ('<USERNAME>', '<PASSWORD>')

# Enter your own NSX-V Manager FQDN
nsx_mgr = 'https://<NSX MANAGER IP / FQDN>' 

central_cli_url = '/api/1.0/nsx/cli?action=execute'  
full_url = str(nsx_mgr) + str(central_cli_url)

### Retrieve all dfw enabled clusters in the environment ###
xml = """<?xml version='1.0' encoding='utf-8'?><nsxcli><command>show cluster all</command></nsxcli>"""
cli_request = s.post(full_url, headers={'Content-Type': 'application/xml', 'Accept': 'text/plain'}, data=xml)
cli_request_results = json.dumps(cli_request.text)

def Convert(string): 
    dfw_list = list(string.split(" ")) 
    return dfw_list

match_cluster = [s for s in (Convert(cli_request_results)) if "domain-" in s]

### Retrieve all hosts in each cluster ###
for i in match_cluster:
    xml = """<?xml version='1.0' encoding='utf-8'?><nsxcli><command>show dfw cluster """ + i + """ </command></nsxcli>"""
    cli_request = s.post(full_url, headers={'Content-Type': 'application/xml', 'Accept': 'text/plain'}, data=xml)
    cli_request_results = json.dumps(cli_request.text)
    match_hosts = [s for s in (Convert(cli_request_results)) if "host-" in s]
    
    ### Retrieve all filters present on each host ###
    for i in match_hosts:
        xml = """<?xml version='1.0' encoding='utf-8'?><nsxcli><command>show dfw host """ + i + """ getfilters</command></nsxcli>"""
        cli_request = s.post(full_url, headers={'Content-Type': 'application/xml', 'Accept': 'text/plain'}, data=xml)
        cli_request_results = json.dumps(cli_request.text)
        #match_filters = [s for s in (Convert(cli_request_results))]  
        match_filters = [s for s in (Convert(cli_request_results)) if "-sfw.2" in s]     
        
        ### Retrieve discovered IP's on filters ###
        for f in match_filters:
            xml = """<?xml version='1.0' encoding='utf-8'?><nsxcli><command>show dfw host """ + i + """ filter """ + f[:-4] + """ discoveredips</command></nsxcli>"""
            cli_request = s.post(full_url, headers={'Content-Type': 'application/xml', 'Accept': 'text/plain'}, data=xml)
            cli_request_results = json.dumps(cli_request.text)
            print(cli_request_results)
