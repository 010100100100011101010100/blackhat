import socket

import paramiko.ssh_exception

import paramiko
import paramiko
import sys
import threading
import subprocess

host_key=paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event=threading.Event()
    def check_channel(self,kind,chan):
        if kind=="session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self,username,password):
        if(username=="justin" and password=="ilovepussy"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    


server=sys.argv[1]
ssh_port=int(sys.argv[2])
try:
    socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    socket.bind((server,ssh_port))
    socket.listen(100)
    print("+ Listening for connection on port %d" % ssh_port)
    client,addr=socket.accept()
    print("+ Connection from %s:%d" % (addr[0],addr[1]))
except Exception as e:
    print(str(e))
    sys.exit(1)
try:
    bh_session=paramiko.Transport(client) #SSH transport layer
    bh_session.add_server_key(host_key)
    server=Server()
    try:
        bh_session.start_server(server=server)
    except paramiko.SSHException as e:
        print("[-] SSH negotiation failed: %s" % str(e))
        sys.exit(1)
    chan=bh_session.accept(20)
    print("Authenticated")
    if chan is None:
        print("No channel")
        sys.exit(1)
    chan.send("Welcome to bh_ssh")
    while True:
        try:
            command=input("Enter command: ").strip("\n")
            if command.lower()=="exit":
                print("exiting")
                bh_session.close()
        except KeyboardInterrupt:
            print("exiting")
            bh_session.close()
            sys.exit(0)
        except Exception as e:
            print("Error reading command: %s" % str(e))
            try:
                bh_session.close()
            except Exception as e:
                pass
            sys.exit(1)
except:
    print("Unable to run")




# ┌────────────┐          ┌──────────┐          ┌───────────────┐        ┌─────────────┐
# │  Operator  │          │  Socket  │          │ Paramiko SSH  │        │  Client SSH │
# └────┬───────┘          └────┬─────┘          └────┬──────────┘        └────┬────────┘
#      │                        │                     │                          │
#      │ Run script             │                     │                          │
#      │ host, port             │                     │                          │
#      │──────────────────────▶│                     │                          │
#      │                        │ Create TCP socket   │                          │
#      │                        │ Bind, listen        │                          │
#      │                        │ Accept connection ◀───────────────────────────┘
#      │                        │                     │
#      │                        │ Pass socket to ─────▶ Paramiko.Transport()
#      │                        │                     │
#      │                        │                     │ Start SSH negotiation
#      │                        │                     │ Add host key
#      │                        │                     │ Accept credentials ◀───┐
#      │                        │                     │                       │
#      │                        │                     │ Check username/pass  │
#      │                        │                     │ if valid → success   │
#      │                        │                     └─────────────┬────────┘
#      │                        │ Create SSH Channel  ◀──────────────┘
#      │                        │ Send welcome msg    ▶ Channel
#      │                        │                     │
#      │ Enter commands         │                     │
#      │────────────────────────▶ Send command       ▶│
#      │                        │                     │
#      │                        │  (loop continues)   │
#      │                        │ if "exit" → close   │
#      │                        │                     │
#      │ Ctrl+C or error        │ Close connection    │
#      │────────────────────────▶ Cleanup & exit      │


