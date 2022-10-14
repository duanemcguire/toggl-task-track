#togglTaskStartStop.py
#
# Query the status of the Shop Lights
# If they have changed on/off status since the last check
# Either (if lights came on) start a generic "Lights On" time track in Toggl/Track
# Or (if lights went off) stop the current time tracker in Toggl/Track


import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import requests
from base64 import b64encode
from datetime import datetime


toggl_auth = os.getenv("TOGGL_AUTH").encode()  # TOGGL_AUTH is <email>:<password>
toggl_workspace = int(os.getenv("TOGGL_WORKSPACE")) #  integer workspace id at toggl.com
toggl_shop_general = int(os.getenv("TOGGL_SHOP_GENERAL")) # integer project_id for my "shop general" project
shop_lights_status_file = os.getenv("SHOP_LIGHTS_STATUS_FILE") # string file location of status file


# Default status.  Will check ISY below and reset if on.
shop_lights_on = False
prior_shop_lights_on = False
# Get prior status - shop_lights_status_file will have one of two words:  on|off
with open(shop_lights_status_file) as f:
    prior_shop_lights_on = f.read() == "on"

# local address for the ISY device is kept in /etc/hosts
ISYaddr = "http://isy"


# Get current info from isy944i
# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
top_level_url = ISYaddr
user_name = os.getenv("ISY_USER")
user_pass = os.environ.get("ISY_PASS")
password_mgr.add_password(None, top_level_url, user_name, user_pass)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# use the opener to fetch a URL
opener.open(ISYaddr)

# Install the opener.
urllib.request.install_opener(opener)
response = urllib.request.urlopen(ISYaddr + "/rest/nodes")
data = response.read()
root = ET.fromstring(data)
onCount = 0
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
                onCount = onCount + 1
            if int(status) > 0 and name == "Shop 2":
                onCount = onCount + 1
            if onCount > 1:
                shop_lights_on = "on"
        except Exception as e:
            print(str(e))
            print(property[0].attrib)
            templateError = str(e)

print("current", shop_lights_on)
print("prior", prior_shop_lights_on)

# Store shop lights status for toggle comparison next time
with open(shop_lights_status_file, "w") as f:
    f.write("on") if shop_lights_on else f.write("off")


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


    data = requests.post(
        "https://api.track.toggl.com/api/v9/workspaces/" + str(toggl_workspace) + "/time_entries",
        json=j,
        headers={
            "content-type": "application/json",
            "Authorization": "Basic %s" % b64encode(toggl_auth).decode("ascii"),
        },
    )
    print(data.json())
if  not shop_lights_on and prior_shop_lights_on:
    # Get current Time entry
    data = requests.get(
        "https://api.track.toggl.com/api/v9/me/time_entries/current",
        headers={
            "content-type": "application/json",
            "Authorization": "Basic %s" % b64encode(toggl_auth).decode("ascii"),
        },
    )
    jdata = data.json()
    workspace = jdata["workspace_id"]
    time_id = jdata["id"]
    # Stop current Time entry
    data = requests.patch(
        "https://api.track.toggl.com/api/v9/workspaces/"
        + str(workspace)
        + "/time_entries/"
        + str(time_id)
        + "/stop",
        headers={
            "content-type": "application/json",
            "Authorization": "Basic %s" % b64encode(toggl_auth).decode("ascii"),
        },
    )
