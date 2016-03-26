# coding: utf-8
from socket import *
from json import loads, dumps
def get_server_info():
        # Origin: https://github.com/teeworlds/teeworlds/blob/master/scripts/tw_api.py
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(("127.0.0.1", 8303))
        sock.send(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x67\x69\x65\x33\x05')
        data, addr = sock.recvfrom(1400)
        sock.close()
        data = data[14:]  # skip header
        slots = data.split(b"\x00")
        server_info = {}
        server_info["token"] = slots[0].decode('utf-8')
        server_info["version"] = slots[1].decode('utf-8')
        server_info["name"] = slots[2].decode('utf-8')
        server_info["map"] = slots[3].decode('utf-8')
        server_info["gametype"] = slots[4].decode('utf-8')
        server_info["flags"] = int(slots[5])
        server_info["num_players"] = int(slots[6])
        server_info["max_players"] = int(slots[7])
        server_info["num_clients"] = int(slots[8])
        server_info["max_clients"] = int(slots[9])
        server_info["players"] = []
        for i in range(0, server_info["num_clients"]):
            player = {}
            player["name"] = slots[10 + i * 5].decode('utf-8')
            player["clan"] = slots[10 + i * 5 + 1].decode('utf-8')
            player["country"] = int(slots[10 + i * 5 + 2])
            player["score"] = int(slots[10 + i * 5 + 3])
            if int(slots[10 + i * 5 + 4]):
                player["player"] = True
            else:
                player["player"] = False
            server_info["players"].append(player)
        return server_info

#inf = get_server_info3("185.112.157.5")
#print(dumps(inf, indent=3))
