import socket
import requests

def spin():
    while True:
        pass


def log_info(*values):
    print(*values)


def get_local_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname()+'.local')
    except socket.gaierror:
        return socket.gethostbyname(socket.gethostname())

def get_public_ip_address():
    resp= requests.get('https://api.ipify.org')
    if resp.status_code == 200:
        return resp.text
    resp= requests.get('https://ifconfig.me/ip')
    if resp.status_code == 200:
        return resp.text