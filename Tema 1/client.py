import glob
import socket
from threading import Thread
import os
import time
import struct


HOST = '127.0.0.1'
PORT = 8081
BUFFER_SIZE = 1024
PATH = "cats_images"


class Client(Thread):
    def __init__(self,protocol,type):
        Thread.__init__(self)
        self.protocol=protocol
        self.type=type

    def run(self):
        if self.protocol=="udp" :
            self.udp_client()
        else:
            self.tcp_client()


    def tcp_client(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_sock.connect((HOST, PORT))
        except Exception as e:
            print("Cannot connect to the server:", e)
        print("Connected")

        while True:
            messages_no = 0
            file_no=0
            total_data=0
            elapsed_time=0

            #send files in folder, one by one
            for f in glob.glob(PATH + "/*.jpg"):
                file_no+=1
                print(file_no)

                file_size=os.path.getsize(f)
                file_name=os.path.basename(f)
                #
                client_sock.send(struct.pack('!I', file_size))
                client_sock.send(file_name.encode('utf-8'))

                file = open(f, 'rb')
                data = file.read(BUFFER_SIZE)
                data_sent = len(data)

                while data:
                    start_time = time.clock()
                    client_sock.sendall(data)

                    if self.type=="ack":
                        while client_sock.recv(4).decode()!="ack":
                            print("message not sent")
                            pass

                    end_time=time.clock()
                    elapsed_time+=(end_time-start_time)
                    data = file.read(BUFFER_SIZE)

                    data_sent+= len(data)
                    messages_no += 1

                total_data += data_sent
                file.close()

                #wait for acknowledgement that entire file was sent before sending another
                if self.type=="noack":
                    while(client_sock.recv(4).decode()!="sent"):
                        print("not sending")
                        pass

            print('Client sent', round(total_data/pow(1024,2),2), "MB")
            print('Client sent', messages_no, "messages")
            print("Elapsed time:", round(elapsed_time, 2),"seconds")
            client_sock.close()
            break



    def udp_client(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.connect((HOST, PORT))

        while True:
            elapsed_time=0
            messages_no = 0
            file_no = 0
            total_data = 0

            # send files in folder, one by one
            for f in glob.glob(PATH + "/*.jpg"):
                file_no += 1
                print(file_no)

                file = open(f, 'rb')
                data = file.read(BUFFER_SIZE)
                data_sent = len(data)

                while data:
                    start_time = time.clock()
                    client_sock.sendto(data, (HOST, PORT))
                    #print(data_sent)
                    if self.type=="ack":
                        while client_sock.recvfrom(BUFFER_SIZE)[0].decode() != "ack":
                            pass

                    end_time = time.clock()
                    elapsed_time += (end_time - start_time)

                    data = file.read(BUFFER_SIZE)

                    data_sent += len(data)
                    messages_no += 1

                total_data += data_sent
                file.close()

            print('Client sent', round(total_data / pow(1024,2), 2), "MB")
            print('Client sent', messages_no, "messages")
            print("Elapsed time:", round(elapsed_time, 2), "seconds")
            client_sock.close()
            break


# print("Choose protocol:\n1. UDP\n2. TCP")
# protocol=input()
#
# print("Choose type:\n1. With ACK\n2. No ACK")
# type=input()
#
# if protocol=="1":
#     if type=="1" :
#         client = Client("udp","ack")
#     else:
#         client = Client("udp", "noack")
# else:
#     if type == "1":
#         client = Client("tcp","ack")
#     else:
#         client = Client("tcp", "noack")
#
# client.start()