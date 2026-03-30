import time
import json
import requests
from mcrcon import MCRcon

# =========================
# CONFIGURATION
# =========================

# RCON VARIABLES
RCON_HOST = "srv1533907.hstgr.cloud"
RCON_PASSWORD = "v3D3hT3buC_tfarc3n1M"
RCON_PORT = 25575

# PATREON VARIABLES
PATREON_TOKEN = "_4OzZLqR37DvvoI41guxMPsomKZHniimpIn2h12GJeM"
CAMPAIGN_ID = "5171342"  # Your Patreon campaign ID

# TIER THRESHOLDS (in cents)
HERO_THRESHOLD = 300
LEGEND_THRESHOLD = 800

# STORAGE COMMAND TEMPLATE
PATREON_SCORE_COMMAND = 'scoreboard players set {player} patreon_tier {tier}'


# =========================
# FUNCTIONS
# =========================

def send_command(cmd):
    """Send a command to Minecraft via RCON"""
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(cmd)
            print(f"[RCON] Command sent: {cmd}")
            print(f"[RCON] Response: {response}")
    except Exception as e:
        print("[RCON] Error sending command:", e)


def fetch_patreon_members():
    """Retrieve active Patreon members with emails and current pledge"""
    members = []
    url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{CAMPAIGN_ID}/members"
    headers = {"Authorization": f"Bearer {PATREON_TOKEN}"}
    params = {
        "fields[member]": "email,full_name,patron_status,currently_entitled_amount_cents,is_free_trial,is_gifted,last_charge_status",
        "page[size]": 100
    }

    while url:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print("[Patreon] Error fetching members:", resp.status_code, resp.json())
            return members
        data = resp.json()
        for m in data.get("data", []):
            attrs = m.get("attributes", {})
            email = attrs.get("email")
            status = attrs.get("patron_status")
            amount = attrs.get("currently_entitled_amount_cents")
            free_trial = attrs.get("is_free_trial", False)
            gifted = attrs.get("is_gifted", False)

            if status == "active_patron" and email and not free_trial and not gifted:
                members.append({
                    "email": email.lower(),
                    "amount": amount
                })
        # Pagination
        url = data.get("links", {}).get("next")

    return members


def check_email_and_set_score(player_name, email_input, members):
    """Check the email submitted by the player and set Minecraft score accordingly"""
    email_input = email_input.lower()
    tier = 0  # Default = non-member
    for m in members:
        if m["email"] == email_input:
            amount = m["amount"]
            if amount >= LEGEND_THRESHOLD:
                tier = 2
            elif amount >= HERO_THRESHOLD:
                tier = 1
            break

    send_command(PATREON_SCORE_COMMAND.format(player=player_name, tier=tier))
    print(f"[Auth] Player {player_name} linked email '{email_input}' -> tier {tier}")


# =========================
# MAIN LOOP
# =========================

if __name__ == "__main__":
    while True:
        print("[Auth] Fetching active Patreon members...")
        members = fetch_patreon_members()
        print(f"[Auth] Found {len(members)} active members with emails")

        # Example: process newly joined players from Minecraft storage
        # Replace this part with your RCON storage query for submitted emails
        # For testing purposes, let's hardcode one:
        test_player_name = "CubePlayer"
        test_email_input = "example@patreon.com"

        check_email_and_set_score(test_player_name, test_email_input, members)

        print("[Auth] Sleeping 30 seconds before next check...")
        time.sleep(30)