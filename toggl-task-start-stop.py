#togglTaskStartStop.py

# Query the status of the Shop Lights
# If they have changed on/off status since the last check
# Either (if lights came on) start a generic "Lights On" time track in Toggl/Track
# Or (if lights went off) stop the current time tracker in Toggl/Track


import xml.etree.ElementTree as ET
import json
import os
import requests
from datetime import datetime

isy_user_name = os.getenv("ISY_USER")
isy_user_pass = os.getenv("ISY_PASS")
toggl_user = os.getenv("TOGGL_USER")
toggl_pass = os.getenv("TOGGL_PASS")
toggl_workspace = int(os.getenv("TOGGL_WORKSPACE")) #  integer workspace id at toggl.com
toggl_shop_general = int(os.getenv("TOGGL_SHOP_GENERAL")) # integer project_id for my "shop general" project
shop_lights_status_file = os.getenv("SHOP_LIGHTS_STATUS_FILE") # string file location of status file
toggl_api_url = "https://api.track.toggl.com/api/v9"


# Default status.  Will check ISY below and reset if on.
shop_lights_on = False
prior_shop_lights_on = False
# Get prior status - shop_lights_status_file will have one of two words:  on|off
with open(shop_lights_status_file) as f:
    prior_shop_lights_on = f.read() == "True"

# local address for the ISY device is kept in /etc/hosts
isy_addr = "http://isy/rest/nodes"


# Get current info from isy944i

response = requests.get(
    isy_addr,
    auth=(isy_user_name,isy_user_pass)
)
root = ET.fromstring(response.content)
on_count = 0
for node in root:
    device = node.attrib.get("nodeDefId")
    if (
        device == "RelayLampSwitch_ADV"
        or device == "DimmerLampSwitch_ADV"
        or device == "RelayLampOnly"
    ):
        try:
            name = node.findall("name")[0].text
            status = node.findall("property")[0].attrib.get("value")
            if int(status) > 0 and name == "Shop 1":
                on_count += 1
            if int(status) > 0 and name == "Shop 2":
                on_count +=  1
            if on_count > 1:
                shop_lights_on = True
        except Exception as e:
            print(str(e))
            print(property[0].attrib)
            templateError = str(e)

print("current", shop_lights_on)
print("prior", prior_shop_lights_on)

# Store shop lights status for toggle comparison next time
with open(shop_lights_status_file, "w") as f:
    f.write(str(shop_lights_on))

# Finally, start or stop a Toggl time entry if the shop lights status has changed. 

if shop_lights_on and not prior_shop_lights_on:
    # Create Toggl time entry
    dt = datetime.utcnow()
    dt = dt.replace(microsecond=0)
    dtstr = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    offset = -int(dt.timestamp())
    j = {
        "created_with": "Shop Lights App",
        "description": "Lights On",
        "project_id": toggl_shop_general,
        "duration": offset,
        "start": dtstr,
        "workspace_id": toggl_workspace,
        "pid": None,
        "tid": None,
        "tags": [],
        "billable": False,
        "wid": 1,
        "stop": None,
    }

    url = "/".join((
        toggl_api_url,
        "workspaces",
        str(toggl_workspace),
        "time_entries"
    ))
    
    requests.post(
        url, 
        json=j, 
        auth=(toggl_user,toggl_pass) 
        )

if  not shop_lights_on and prior_shop_lights_on:
    # Get current Time entry
    data = requests.get(
        toggl_api_url + "/me/time_entries/current",
        auth=(toggl_user,toggl_pass) 
    )
    jdata = data.json()
    if len(jdata) :
        workspace = jdata["workspace_id"]
        time_id = jdata["id"]
        url = "/".join((
            toggl_api_url,
            "workspaces",
            str(toggl_workspace),
            "time_entries",
            str(time_id),
            "stop"
        ))  
        # Stop current Time entry
        requests.patch(
            url,
            auth=(toggl_user,toggl_pass)
        )
        
