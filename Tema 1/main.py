import client as cl
import server as sv

print("Choose protocol:\n1. UDP\n2. TCP")
protocol=input()

print("Choose type:\n1. With ACK\n2. No ACK")
type=input()
print(type)
if protocol=="1":
    if type=="1" :
        server = sv.Server("udp","ack")
        client = cl.Client("udp","ack")
    else:
        server = sv.Server("udp", "noack")
        client = cl.Client("udp", "noack")
else:
    if type == "1":
        server = sv.Server("tcp","ack")
        client = cl.Client("tcp","ack")
    else:
        server = sv.Server("tcp", "noack")
        client = cl.Client("tcp", "noack")

server.start()
client.start()
