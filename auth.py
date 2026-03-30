import time
import json
import requests
import re
from mcrcon import MCRcon

# =========================
# CONFIGURATION
# =========================

RCON_HOST = "srv1533907.hstgr.cloud"
RCON_PASSWORD = "v3D3hT3buC_tfarc3n1M"
RCON_PORT = 25575

PATREON_TOKEN = "_4OzZLqR37DvvoI41guxMPsomKZHniimpIn2h12GJeM"
CAMPAIGN_ID = "5171342"

# Tier thresholds (in cents)
HERO_THRESHOLD = 300
LEGEND_THRESHOLD = 800


# =========================
# RCON FUNCTION
# =========================

def send_command(cmd):
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            return mcr.command(cmd)
    except Exception as e:
        print("[RCON ERROR]", e)
        return None


# =========================
# GET MINECRAFT STORAGE
# =========================

def get_patreon_links():
    raw = send_command("data get storage jojo_recubed patreon")

    if not raw:
        return []

    print("\n[MC RAW STORAGE]")
    print(raw)

    # Extract JSON-like NBT
    match = re.search(r'\{.*\}', raw)
    if not match:
        print("[Parse] No valid data found")
        return []

    nbt = match.group(0)

    # Convert NBT → JSON
    nbt = re.sub(r'(\w+):', r'"\1":', nbt)  # add quotes to keys
    nbt = nbt.replace("'", '"')            # normalize quotes

    try:
        data = json.loads(nbt)
    except Exception as e:
        print("[Parse ERROR]", e)
        return []

    # Structure: {data:[{player,mail}]}
    links = data.get("data", [])

    print(f"[Parse] Found {len(links)} linked players\n")

    return links


# =========================
# FETCH PATREON MEMBERS
# =========================

def fetch_patreon_members():
    members = []

    url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{CAMPAIGN_ID}/members"
    headers = {"Authorization": f"Bearer {PATREON_TOKEN}"}
    params = {
        "fields[member]": "email,full_name,patron_status,currently_entitled_amount_cents",
        "page[size]": 100
    }

    while url:
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code != 200:
            print("[Patreon ERROR]", resp.status_code, resp.json())
            return members

        data = resp.json()

        for m in data.get("data", []):
            attr = m.get("attributes", {})

            email = attr.get("email")
            status = attr.get("patron_status")
            amount = attr.get("currently_entitled_amount_cents", 0)

            if status == "active_patron" and email:
                members.append({
                    "email": email.lower(),
                    "amount": amount
                })

        url = data.get("links", {}).get("next")

    # DEBUG PRINT
    print("\n[Patreon] Active Members:")
    print("{:<35} {:<10}".format("Email", "Cents"))
    print("-" * 50)

    for m in members:
        print("{:<35} {:<10}".format(m["email"], m["amount"]))

    print("-" * 50)
    print(f"[Patreon] Total Active Members: {len(members)}\n")

    return members


# =========================
# TIER CALCULATION
# =========================

def get_tier(amount):
    if amount >= LEGEND_THRESHOLD:
        return 2
    elif amount >= HERO_THRESHOLD:
        return 1
    return 0


# =========================
# MAIN LOOP
# =========================

if __name__ == "__main__":
    while True:
        print("\n============================")
        print("[Auth] New cycle")
        print("============================")

        # 1. Fetch Patreon members
        members = fetch_patreon_members()

        # Fast lookup dictionary
        member_lookup = {m["email"]: m["amount"] for m in members}

        # 2. Get Minecraft linked players
        links = get_patreon_links()

        # 3. Match and assign tiers
        for entry in links:
            player = entry.get("player")
            email = entry.get("mail", "").lower()

            if not player or not email:
                continue

            amount = member_lookup.get(email, 0)
            tier = get_tier(amount)

            cmd = f"scoreboard players set {player} patreon_tier {tier}"
            send_command(cmd)

            print(f"[Auth] {player} ({email}) -> tier {tier}")

        print("\n[Auth] Sleeping 30 seconds...\n")
        time.sleep(30)