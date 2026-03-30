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
headers = {"Authorization": f"Bearer {PATREON_TOKEN}"}
CAMPAIGN_ID = "5171342"

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
    #url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{CAMPAIGN_ID}/members?include=currently_entitled_tiers&page[size]=100"
    url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{CAMPAIGN_ID}/members?fields[member]=email,full_name,patron_status,currently_entitled_amount_cents,is_free_trial,is_gifted,last_charge_status&page[size]=100"
    resp = requests.get(url, headers=headers)
    
    print("Status code:", resp.status_code)
    print(resp.json())

    #if resp.status_code == 200:
    #    data = resp.json()
    #    for member in data.get("data", []):
    #        email = member["attributes"].get("email")
    #        status = member["attributes"].get("patron_status")
    #        amount = member["attributes"].get("currently_entitled_amount_cents")
    #        print(f"Email: {email}, Status: {status}, Amount (cents): {amount}")
    #else:
    #    print(resp.json())
    #url = "https://www.patreon.com/api/oauth2/v2/campaigns?include=memberships"
    #headers = {"Authorization": f"Bearer {PATREON_TOKEN}"}
    #resp = requests.get(url, headers=headers)
    #print(resp.status_code)
    #print(resp.json())
    time.sleep(30)