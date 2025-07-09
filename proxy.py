import socket
import sys
import threading


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join([f"{ord(c):0{digits}X}" if isinstance(c, str) else f"{c:0{digits}X}" for c in s])
        text = ''.join([chr(c) if 32 <= c < 127 else '.' for c in s])
        result.append(f"{i:04X}   {hexa:<{length*3}}   {text}")
    print('\n'.join(result))

def receive_from(connection):
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer


def response_handler(buffer):
    return buffer 


def proxy_handler(client_socket, remote_host, remote_port):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))  

    remote_buffer = receive_from(remote_socket)
    if len(remote_buffer):
        print("[<==] Received from remote")
        hexdump(remote_buffer)
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[==>] Received from client")
            hexdump(local_buffer)
            remote_socket.send(local_buffer)

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received from remote")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)

        if not len(local_buffer) and not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[-] No more data. Closing connections.")
            break

def server_loop(local_host, local_port, remote_host, remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to bind: {e}")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port} → {remote_host}:{remote_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"[==>] Connection from {addr}")
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 4:
        print("Usage: python proxy.py [localhost] [localport] [remotehost] [remoteport]")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    server_loop(local_host, local_port, remote_host, remote_port)

if __name__ == "__main__":
    main()



# ┌────────────┐       ┌────────────┐       ┌───────────────┐
# │   Client   │       │   Proxy    │       │ Remote Server │
# └────┬───────┘       └────┬───────┘       └──────┬────────┘
#      │ Connects to        │                        │
#      │ local_host:port    │                        │
#      │───────────────────▶│                        │
#      │                    │ Accept connection      │
#      │                    │ Start proxy_handler    │
#      │                    │                        │
#      │                    │ Connect to remote_host │
#      │                    │───────────────────────▶│
#      │                    │                        │
#      │                    │ [Receive greeting?]    │
#      │                    │◀───────────────────────│
#      │                    │ Send to client         │
#      │◀───────────────────│                        │
#      │                    │                        │
#      │ Send data          │                        │
#      │───────────────────▶│                        │
#      │                    │ Receive from client    │
#      │                    │ Send to remote         │
#      │                    │───────────────────────▶│
#      │                    │                        │
#      │                    │ Receive from remote    │
#      │                    │◀───────────────────────│
#      │                    │ Send to client         │
#      │◀───────────────────│                        │
#      │                    │ Repeat loop            │
#      │                    │                        │
#      │ (disconnects)      │                        │
#      │───────────────────┐│                        │
#      │                    │                        │
#      │                    │ Close both connections │
#      │                    │───────────────────────▶│
#      │                    │ Done                   │
