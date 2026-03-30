import time
import json
import requests
from mcrcon import MCRcon

# RCON VARIABLES
RCON_HOST = "srv1533907.hstgr.cloud"
RCON_PASSWORD = "v3D3hT3buC_tfarc3n1M"
RCON_PORT = 25575

# PATREON VARIABLES
PATREON_TOKEN = "_4OzZLqR37DvvoI41guxMPsomKZHniimpIn2h12GJeM"

def send_command(cmd):
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(cmd)
            print("Command sent:", cmd)
            print("Response:", response)
    except Exception as e:
        print("Error sending command:", e)

# TEST LOOP
while True:
    #print("Trying to get player storage..")
    #send_command("data get storage jojo_recubed player")
    print("Testing Patreon API..")
    headers = {"Authorization": f"Bearer {PATREON_TOKEN}"}

    # Get campaigns for this creator
    url = "https://www.patreon.com/api/oauth2/v2/campaigns"
    resp = requests.get(url, headers=headers)
    
    print(resp.status_code)
    print(json.dumps(resp.json(), indent=2))
    #url = "https://www.patreon.com/api/oauth2/v2/campaigns?include=memberships"
    #headers = {"Authorization": f"Bearer {PATREON_TOKEN}"}
    #resp = requests.get(url, headers=headers)
    #print(resp.status_code)
    #print(resp.json())
    time.sleep(30)