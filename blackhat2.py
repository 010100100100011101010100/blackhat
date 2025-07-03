#Build a TCP Proxy server (middleman between client and server) - does extra - logging, filtering,modification
import socket 
import sys
import threading 

def server_loop(local_host,local_port,remote_host,remote_port):
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except Exception as e:
        print(f"Failed to bind to {local_host}:{local_port} - {e}")
        sys.exit   (0)
    print(f"Listening on {local_host}:{local_port  } -> {remote_host}:{remote_port}")
    server.listen(5)
    while True:
        client_socket,addr=server.accept()
        print(f"Incoming connection from {addr}")
        proxy_thread=threading.Thread(target=proxy_handler,args=(client_socket,remote_host,remote_port,receive_first=True))
        proxy_thread.start()



def main():
    if len(sys.argv[1:]) != 4:
        print("Usage: python blackhat2.py [localhost] [localport] [remotehost] [remoteport]")
        sys.exit(0)
    local_host=int(sys.argv[1])
    local_port=int(sys.argv[2])
    remote_host=sys.argv[3]
    remote_port=int(sys.argv[4])
    server_loop(local_host, local_port, remote_host, remote_port)


def proxy_handler(client_socket,remote_host,remote_port):
    

