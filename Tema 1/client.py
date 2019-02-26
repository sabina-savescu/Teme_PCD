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
    def __init__(self,protocol):
        Thread.__init__(self)
        self.protocol=protocol

    def run(self):
        if(self.protocol=="udp"):
            self.udp_client()
        else:
            self.tcp_client()


    def tcp_client(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((HOST, PORT))

        while True:
            start_time = time.time()
            messages_no = 0
            file_no=0
            total_data=0
            elapsed_time=0

            #send files in folder, one by one
            for f in glob.glob(PATH + "/*.jpg"):
                file_no+=1
                #print(file_no)

                file_size=os.path.getsize(f)
                file_name=os.path.basename(f)

                client_sock.send(struct.pack('!I', file_size))
                client_sock.send(file_name.encode('utf-8'))

                file = open(f, 'rb')
                data = file.read(BUFFER_SIZE)
                data_sent = len(data)

                while data:
                    start_time = time.clock()
                    client_sock.send(data)
                    end_time=time.clock()
                    elapsed_time+=(end_time-start_time)
                    data = file.read(BUFFER_SIZE)

                    data_sent+= len(data)
                    messages_no += 1

                total_data += data_sent
                file.close()

                #wait for acknowledgement that entire file was sent before sending another
                while(client_sock.recv(1024).decode()!="ack"):
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
                #print(file_no)

                file = open(f, 'rb')
                data = file.read(BUFFER_SIZE)
                data_sent = len(data)

                while data:
                    start_time = time.clock()
                    client_sock.sendto(data, (HOST, PORT))
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



