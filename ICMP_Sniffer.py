import os
from ctypes import *
import struct
import socket
host="192.167.129.12"

class IPHeader(Structure):
    _fields_=[
        ('ihl',c_ubyte,4),#Internet Header Length
        ('version',c_ubyte,4),#IP Version
        ('tos',c_ubyte),#Type of service
        ('len',c_ushort),#Total Length
        ('id',c_ushort),#Identification
        ('offset',c_ushort),#Fragment Offset
        ('ttl',c_ubyte),#Time to Live
        ('protocol_num',c_ubyte),#Protocol
        ('sum',c_ushort),#Header Checksum
        ('src',c_ulong),#Source Address
        ('dst',c_ulong)#Destination Address

    ]

    def __new__(self,socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    def __init__(self,socket_buffer=None):
        self.protocol_mapping= {1:"ICMP",6:"TCP",17:"UDP"}
        self.src=socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst=socket.inet_ntoa(struct.pack("<L",self.dst))
        try:
            self.protocol=self.protocol_mapping[self.protocol_num]
        except:
            return None

class ICMP(Structure):
    _fields_=[
        ('type',c_ubyte,8),#Type of ICMP message
        ('code',c_ubyte,8),#Code
        ('checksum',c_ushort,16),#Checksum
        ('unused',c_ushort,16),#Unused
        ('next_hop_mtu',c_ushort,16)#Next hop MTU
    ]

    def __new__(self,socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    def __init__(self,socket_buffer=None):
        pass


if os.name=="nt":
    socket_protocol=socket.IPPROTO_IP
else:
    socket_protocol=socket.IPPROTO_ICMP

sniffer=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket_protocol)
sniffer.bind((host,0))
sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)

if os.name=='nt':
    sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

try:
    while True:
        raw_buffer=sniffer.recvfrom(65565)[0]
        ip_header=IPHeader(raw_buffer[:20])
        if (ip_header.protocol=="IP"):
            
            print("Protocol: %s" % ip_header.protocol)
        else:
            offset=ip_header.ihl*4
            buf=raw_buffer[offset:offset+sizeof(ICMP)]
            icmp_header=ICMP(buf)
            print("ICMP Type: %d Code: %d Checksum: %d" % (icmp_header.type, icmp_header.code, icmp_header.checksum))

except  KeyboardInterrupt:
    if os.name=='nt':
        sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)#Switiching off promiscous mode
    print("Exiting Sniffer")



# ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
# │   Network    │         │  Python App  │         │  OS / Socket │
# └────┬─────────┘         └────┬─────────┘         └────┬─────────┘
#      │ Send packet              │                        │
#      ├─────────────────────────▶│                        │
#      │                          │ Create raw socket      │
#      │                          │───────────────────────▶│
#      │                          │ Bind to IP             │
#      │                          │ Set header include     │
#      │                          │ Set promiscuous mode   │
#      │                          │◀───────────────────────┘
#      │                          │
#      │                          │ Loop: recvfrom() packet
#      │                          │◀───────────────────────┐
#      │                          │                        │
#      │                          │ IPHeader ← first 20 bytes
#      │                          │ Parse version, proto, src/dst
#      │                          │
#      │      if protocol == ICMP │
#      │                          │ Offset = ihl * 4       │
#      │                          │ Parse ICMP header      │
#      │                          │ Print Type, Code, Checksum
#      │                          │
#      │                          │ Else: print protocol    │
#      │                          │
#      │                          │ Wait for next packet   │
#      │                          │
#      │ Ctrl+C                   │                        │
#      │────────────────────────▶│                        │
#      │                          │ Cleanup: disable RCVALL│
#      │                          │ Exit                   │
