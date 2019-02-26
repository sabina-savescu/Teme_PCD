import client as cl
import server as sv

print("Choose protocol:\n1. UDP\n2. TCP")

protocol=input()
if(protocol=="1"):
    server = sv.Server("udp")
    client = cl.Client("udp")
else:
    server = sv.Server("tcp")
    client = cl.Client("tcp")

server.start()
client.start()
