#!/usr/bin/python

#imports
import requests
import json
import sys
import time

#Import the CRED module from a separate directory
import cred

#custom variables for the program imported from the cred.py file located in the same directory
organization = cred.organization
key = cred.key
hub = cred.hub

output = open("output.txt", "w", 0)

#Main URL for the Meraki Platform
dashboard = "https://dashboard.meraki.com/api/v0"
#api token and other data that needs to be uploaded in the header
headers = {'X-Cisco-Meraki-API-Key': (key), 'Content-Type': 'application/json'}

#pull back the network id and s/n of devices for a network
get_networks_url = dashboard + '/organizations/%s/networks' % organization
get_networks_response = requests.get(get_networks_url, headers=headers)
get_networks_json = get_networks_response.json()

for network_id in get_networks_json:
    time.sleep(1)
    get_device_sn_url = dashboard + '/networks/%s/devices' % network_id["id"]
    get_device_sn_response = requests.get(get_device_sn_url, headers=headers)
    get_device_sn_json = get_device_sn_response.json()
    if get_device_sn_response.status_code == 200:
        for device_sn in get_device_sn_json:
            #Sites I don't want to rename, so that this script can be reused without affecting the names of devices I don't want touched.
            try:
                if network_id["name"] == "CA-HQ" or network_id["name"] == "TNDC" or network_id["name"] == "TNDC3":
                    continue
                else:
                    try:
                        time.sleep(1)
                        update_device_url = dashboard + '/networks/%s/devices/%s' % (network_id["id"], device_sn["serial"])
                        update_device_url_response = requests.get(update_device_url, headers=headers)
                        update_device_url_json = update_device_url_response.json()
                        output.write(str(network_id["name"]) + " " + update_device_url_json["name"] + " " + update_device_url_json["notes"] + "\n")
                    except KeyError:
                        try:
                            output.write(str(network_id["name"]) + " " + update_device_url_json["name"] + " Store has no notes" + "\n")
                            continue
                        except KeyError:
                            output.write(str(network_id["name"]) + " Store needs name updated" + "\n")
                            continue
            except TypeError:
                output.write(network_id["name"] + "errored out" + "\n") 
                continue
    else:
        output.write(network_id["name"] + "errored out" + "\n")   
        time.sleep(30)
        continue

output.close
