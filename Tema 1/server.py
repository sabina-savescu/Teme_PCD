import socket
from threading import Thread


HOST = '127.0.0.1'
PORT = 8081
BUFFER_SIZE = 1024
PATH = "server_cats"

class Server(Thread):
    def __init__(self,protocol,type):
        Thread.__init__(self)
        self.protocol=protocol
        self.type=type

    def run(self):
        if self.protocol=="udp" :
            self.udp_server()
        else:
            self.tcp_server()

    def tcp_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((HOST, PORT))

        #set number of connections
        server_sock.listen(5)
        print ('Server TCP listening....')

        client_no = 0
        while True:
            conn, addr = server_sock.accept()
            client_no+=1
            messages_no = 0
            total_data=0

            print("Client number:",client_no,", got connection from ", addr)


            while True:
                try:
                    file_size=conn.recv(4)
                    if not file_size:
                        break
                    file_size = int.from_bytes(file_size, byteorder='big')

                    file_name = conn.recv(16)
                    file_name=file_name.decode('utf-8').strip()

                    file = open(PATH+"/"+file_name, 'wb')  # open as binary data

                    data_recv = 0
                    while (data_recv<file_size):

                        data = conn.recv(BUFFER_SIZE)
                        if not data:
                            break
                        else:
                            if self.type=="ack":
                                conn.sendall("ack".encode())
                            file.write(data)
                            data_recv+=len(data)
                            messages_no += 1

                    total_data+=data_recv
                    file.close()

                    if self.type=="noack":
                        conn.sendall("sent".encode())

                except socket.error:
                    print("Socket error")
                    break

            conn.close()
            print("Connection closed.")
            print('Server received', round(total_data/pow(1024,2),2), "MB")
            print('Server received', messages_no, "messages")



    def udp_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind((HOST, PORT))

        print("Server UDP")
        messages_no = 0
        total_data = 0
        server_sock.settimeout(5)

        while True:
            try:
                data, addr = server_sock.recvfrom(BUFFER_SIZE)
                if self.type=="ack":
                    server_sock.sendto("ack".encode(), addr)
                messages_no += 1
                total_data += len(data)

            except socket.error:
                print('Server received', round(total_data / pow(1024, 2), 2), "MB")
                print('Server received', messages_no, "messages")



# print("Choose protocol:\n1. UDP\n2. TCP")
# protocol=input()
#
# print("Choose type:\n1. With ACK\n2. No ACK")
# type=input()
#
# if protocol=="1":
#     if type=="1" :
#         server = Server("udp","ack")
#     else:
#         server = Server("udp", "noack")
# else:
#     if type == "1":
#         server = Server("tcp","ack")
#     else:
#         server = Server("tcp", "noack")
#
# server.start()