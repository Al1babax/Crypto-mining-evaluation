import WS_coolparcel as ws

addresses = ws.init("China", "Finland", {"weight": "28.0", "length": "11.0", "width": "11.0", "height": "11.0"})
#for address in addresses:
#    print(address)
len(addresses)
#print("others")
#print(addresses[0]["cost"][1:])

