import socket
import sys
import getopt
import threading
import subprocess
#TCP
target_host="www.google.com"
target_port=80

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((target_host,target_port))

client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

response=client.recv(4096)

print(response)


#UDP
target_host='127.0.0.1'
target_port=80
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
print("SENDING THE DATA TO THE SERVER")
client.sendto(b"AAAABBCCC",(target_host,target_port))
data,address=client.recvfrom(4096)

print(data)

#multi threading servers - TCP
bin_ip="0.0.0.0"
binding_port=9999
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((bin_ip,binding_port))
server.listen(5)
def handleClientRequest(client_socket):
    request=client_socket.recv(1024)
    print(f"Received: {request}")
    client_socket.send("ACK!".encode())
    client_socket.close()

while True:
    client,addr=server.accept()
    print(f"Accepted connection from {addr}")
    client_handler=threading.Thread(target=(handleClientRequest),args=(client,))
    client_handler.start()

#Building a netcat similar tool


listen=False
command=False
upload=False
execute=""
target=""
upload_destination=""
port=0

def usage():
    print("BH net tool")
    print()
    print("Usage : blackhat.py -t target host -p port")
    print("-l --listen      =listen on [host]:[port] for incoming connections")
    print("-e --execute     =file_to_run - execute the given file upon receiving a connection")
    print("-c --command     =initialise a command shell")
    print("-u --upload      =destination - upon receiving a connection upload a file and write to [destination]")
    sys.exit(0)

def main():
    global listen
    global command
    global execute
    global upload_destination
    global target 
    global port 


    if not len(sys.argv[1:]):
        usage()
    try:
        opts,args=getopt.getopt(sys.argv[1:],"hle:t:p:c:u:",["help","listen","execute=","target=","port=","command","upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-c","--command"):
            command=True
        elif o in ("-l","--listen"):
            listen  =True
        elif o in ("-e","--execute"):
            execute=a
        elif o in ("-u","--upload"):
            upload_destination=a
        elif o in ("-p","--port"):
            port=int(a)
        else:
            assert False,"Wrong option choosen"
    
    if not listen and port>0 and len(target)>0:
        buffer=sys.stdin.read()
        client_sender(buffer)
    if listen:
        server_loop()
if __name__ == "__main__":
    main()

def client_sender(buffer):
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
        while True:
            recv_len=1
            response=""
            while recv_len:
                data=client.recv(2024)
                recv_len=len(data)
                response+=data
                if recv_len<2024:
                    break
                print(response)
                buffer=raw_input()
                buffer+="\n"
                client.send(buffer)
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        print("Closing client socket")
        client.close()
    
def server_loop():
    global target
    if not len(target):
        target="0.0.0.0"
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    while True:
        client_socket,add=server.accept()
        client_thread=threading.Thread(target=handle_client,args=(client_socket,))
        client_thread.start()


def run_command(command):
    command=command.rstrip()
    try:
        output=subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except Exception as e:
        output=str(e).encode()
    return output



def handle_client(client_socket):
    global upload_destination
    global execute
    global command

    if len(upload_destination):
        file_buffer=""
        while True:
            data=client_socket.recv(1024)
            if not data:
                break
            file_buffer+=data.decode()
        try:
            file=open(upload_destination,"wb")
            file.write(file_buffer.encode())
            file.close()
            clien_socket.send("Successfully saved to the file")
        except Exception as e:
            client_socket.send(f"Failed to save to the file: {e}".encode())

    if len(execute):
        output=run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send(b"Shell> ")
            cmd_buffer=""
            while "\n" not in cmd_buffer:
                cmd_buffer+=client_socket.recv(1024).decode()
            response=run_command(cmd_buffer)
            client_socket.send(response.encode())
    












        
    


