import time
from mcrcon import MCRcon

# REPLACE THESE WITH YOUR DATA
RCON_HOST = "srv1533907.hstgr.cloud"
RCON_PASSWORD = "v3D3hT3buC_tfarc3n1M"
RCON_PORT = 25575

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
    print("Trying to get player storage..")
    send_command("data get storage jojo_recubed player")
    #/data get storage jojo_recubed player
    #send_command("say Backend connected!")
    time.sleep(30)