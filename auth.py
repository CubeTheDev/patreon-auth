import time
import json
import requests
from mcrcon import MCRcon

# =========================
# CONFIGURATION
# =========================

RCON_HOST = "srv1533907.hstgr.cloud"
RCON_PASSWORD = "v3D3hT3buC_tfarc3n1M"
RCON_PORT = 25575

PATREON_TOKEN = "_4OzZLqR37DvvoI41guxMPsomKZHniimpIn2h12GJeM"
CAMPAIGN_ID = "5171342"

HERO_THRESHOLD = 300
LEGEND_THRESHOLD = 800

PATREON_SCORE_COMMAND = 'scoreboard players set {player} patreon_tier {tier}'


# =========================
# FUNCTIONS
# =========================

def send_command(cmd):
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(cmd)
            print(f"[RCON] Command sent: {cmd}")
            print(f"[RCON] Response: {response}")
    except Exception as e:
        print("[RCON] Error sending command:", e)


def fetch_patreon_members():
    """Retrieve active Patreon members with emails and pledge amounts"""
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
            full_name = attrs.get("full_name", "Unknown")
            status = attrs.get("patron_status")
            amount = attrs.get("currently_entitled_amount_cents", 0)
            free_trial = attrs.get("is_free_trial", False)
            gifted = attrs.get("is_gifted", False)

            if status == "active_patron" and email and not free_trial and not gifted:
                members.append({
                    "full_name": full_name,
                    "email": email.lower(),
                    "amount": amount
                })

        # Pagination
        url = data.get("links", {}).get("next")

    # Print all members in a readable log
    print("\n[Patreon] Active members list:")
    print("{:<25} {:<35} {:<10}".format("Name", "Email", "Cents"))
    print("-" * 75)
    for m in members:
        print("{:<25} {:<35} {:<10}".format(m["full_name"], m["email"], m["amount"]))
    print("-" * 75, "\n")

    return members


def check_email_and_set_score(player_name, email_input, members):
    email_input = email_input.lower()
    tier = 0
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
        print(f"[Auth] Found {len(members)} active members with emails\n")

        # Example: process newly joined players from Minecraft storage
        # Replace with actual storage reading in the future
        test_player_name = "CubePlayer"
        test_email_input = "example@patreon.com"

        check_email_and_set_score(test_player_name, test_email_input, members)

        print("[Auth] Sleeping 30 seconds before next check...\n")
        time.sleep(30)