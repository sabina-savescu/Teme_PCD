import socket
from threading import Thread


HOST = '127.0.0.1'
PORT = 8081
BUFFER_SIZE = 1024
PATH = "server_cats"

class Server(Thread):
    def __init__(self,protocol):
        Thread.__init__(self)
        self.protocol=protocol

    def run(self):
        if (self.protocol == "udp"):
            self.udp_server()
        else:
            self.tcp_server()

    def tcp_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((HOST, PORT))

        #set number of connections
        server_sock.listen(1)
        print ('Server TCP listening....')

        client_no = 0
        while True:
            conn, addr = server_sock.accept()
            client_no+=1
            messages_no = 0
            total_data=0
            print("Client number:",client_no,", got connection from ", addr)

            try:
                while True:
                    file_size=conn.recv(4)
                    file_size = int.from_bytes(file_size, byteorder='big')

                    file_name = conn.recv(16)
                    file_name=file_name.decode('utf-8').strip()

                    file = open(PATH+"/"+file_name, 'wb')  # open as binary data

                    data_recv = 0
                    while (data_recv<file_size):

                        data = conn.recv(BUFFER_SIZE)
                        file.write(data)

                        messages_no += 1
                        data_recv+=len(data)

                    #entire file has been sent
                    conn.send("ack".encode())
                    total_data+=data_recv
                    file.close()

            except socket.error:
                conn.close()
                print('Server received', round(total_data/pow(1024,2),2), "MB")
                print('Server received', messages_no, "messages")



    def udp_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind((HOST, PORT))

        print("Server UDP")
        messages_no = 0
        total_data = 0
        server_sock.settimeout(4)
        while True:
            try:
                data = server_sock.recvfrom(BUFFER_SIZE)[0]
                messages_no += 1
                total_data += len(data)
            except socket.error:
                print('Server received', round(total_data / pow(1024, 2), 2), "MB")
                print('Server received', messages_no, "messages")
                break
