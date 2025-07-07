#Forward SSH tunneling

#Command -> ssh -L [local_port]:[remote_host]:[remote_port] [user]@ssh_server
# We are trying to connect from our local_port to remort_port and logging in as user on ssh_server

#anything I send to localhost:8008, forward that through the SSH server sshserver, and then deliver it to the host called web on port 80 (HTTP).
#[Laptop] --(localhost:8008)--> [SSH Tunnel] --> [SSH Server] --(HTTP req)--> [Internal Web Server]

#web in the command is hostname resolvable / othewise add IP in the command

#SAMPLE : ssh -L 8008:mysql.internal:3306 rasesh@sshserver


#In windows , many times it is not possible to spin up SSH server (sshd), so we use reverse SSH Tunneling to get data from reverse SSH server (which is our own device, in that case the Windows middleman becomes reverse SSH Client)

#SAMPLE : ssh -R 8008:localhost:8008 rasesh@sshserver

import getpass
import socket
import select
import sys
from optparse import OptionParser

import paramiko
import paramiko
import threading

SSH_PORT=2
DEFAULT_PORT=4000
g_verbose=True #This is used for debugging purposes


def verbose(s):
    if g_verbose:
        print(s)


def handler(chan,host,port):#chan is the bidirectional SSH channel
    socket=socket.socket()
    try:
        socket.connect((host,port))
    except Exception as e:
        if g_verbose:
            verbose("[-] Connection failed: %s" % str(e))
    if g_verbose:
        verbose("[+] Connected Tunnel Open %r -> %r -> %r" % (chan.origin_addr,chan.getpeername(),(host,port)))  #where traffic originated from, where we have connected via SSH, where we are forwarding to
    
    while True:
        r,w,x=select.select([socket,chan],[],[])
        if socket in r:
            data=socket.recv(1024)
            if len(data)==0:
                break
            chan.send(data)
        if chan in r:
            data=chan.recv(1024)
            if len(data)==0:
                break
            socket.send(data)
    socket.close()
    chan.close()
    verbose("[+] Tunnel closed from %r"%(chan.origin_addr,))




def reverse_forward_tunnel(server_port,remote_host,remote_port,transport):
    transport.request_port_forward("",server_port)
    while True:
        chan=transport.accept(1000)
        if chan is None:
            continue
        thr=threading.Thread(
            target=handler,args=(chan,remote_host,remote_port)
        )
        thr.setDaemon(True)
        thr.start()


def get_host_port(spec,default_port=DEFAULT_PORT):
    if ":" in spec:
        host,port=spec.split(":")
        port=int(port)
        host=host.strip()
        return (host,port)


def parse_options():
    global g_verbose
    
    parser=OptionParser(
        usage="usage: %prog [options] <ssh_server> [:<server-ports>]"
        version="%prog 1.0",
        description=HELP,
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        description="Suppress all informational output"
    )

    parser.add_option(
        "-u",
        "--username",
        action="store",
        type="int",
        dest="port",
        default=DEFAULT_PORT,
        help="SSH server port to connect to (default: %default)"
    )

    parser.add_option(
        "-K",
        "--key",
        action="store",
        dest="keyfile",
        type="string",
        default=None,
        description="private key file to use for SSH Authentication"
    )

    parser.add_option(
        "",
        "--no-key",
        action="store_false",
        dest="use_keyfile",
        default=True,
        description="don't look or use a private key file"
    )

    parser.add_option(
        "-P",
        "--password",
        action="store",
        dest="readpass",
        default=None,
        description="read password from stdin"
    )

    parser.add_option(
        "-r",
        "--remote",
        action="store",
        type="string",
        dest="remote_spec",
        default=None,
        metavar="host:port",
        help="remote host and port to forward to"
    )

    options,args=parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments")
    if options.remote is None:
        parser.error("Remote host and port must be specified")
    g_verbose=options.verbose
    server_host,server_port=get_host_port(args[0],SSH_PORT)
    remote_host,remote_port=get_host_port(options.remote,DEFAULT_PORT)
    return options,(server_host,server_port),(remote_host,remote_port) 


def main():
    options,server,remote=parse_options()
    password=None
    if options.readpass:
        password= getpass.getpass("SSH Password: ")
    client=paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    verbose("Connecting to SSH host %s %d ...."% (server[0],server[1]))
    try:
        client.connect(
            server[0],
            server[1],
            username=options.username,
            key_filename=options.keyfile,
            password=password,
            look_for_keys=options.use_keyfile,
        )
    except Exception as e:
        print("[-] Connection failed: %s" % str(e))
        sys.exit(1)
    verbose("Trying reverse forward tunnel to %s:%d"%(remote[0].remote[1]))
    try:
        reverse_forward_tunnel(
            options.port,remote[0],remote[1],client.get_transport()
        )
    except Exception as e:
        print("[-] Reverse forward tunnel failed: %s" % str(e))
        sys.exit(1)

if __name__=="__main__":
    main()


        
