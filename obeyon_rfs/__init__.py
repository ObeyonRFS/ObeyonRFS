import random
import time
from typing import Any, Dict

from pydantic import BaseModel
import obeyon_rfs.core
import os
import socket
import psutil
import requests

__version__ = '0.0.10'
__module_dir__ = os.path.dirname(__file__)



class InitArgs(BaseModel):
    ORFS_CORE_HOST:str=None
    ORFS_CORE_PORT:int=None

_init_args:InitArgs=None

def init(args:Dict[str,Any]=None):
    if args is None:
        return
    args.setdefault("RFS_CORE_HOST",None)
    if args["RFS_CORE_HOST"] is not None:
        os.environ["RFS_CORE_HOST"] = args["RFS_CORE_HOST"]
    args.setdefault("RFS_CORE_PORT",None)
    if args["RFS_CORE_PORT"] is not None:
        os.environ["RFS_CORE_PORT"] = args["RFS_CORE_PORT"]


def spin_once(period_time=0.001):
    if obeyon_rfs.is_core_running()==False:
        raise ConnectionError("RFS core is not available")
    time.sleep(period_time)
def spin(period_time=0.001):
    while True:
        spin_once(period_time)


def get_core_host():
    RFS_CORE_HOST = os.environ.get("RFS_CORE_HOST")
    if RFS_CORE_HOST is None:
        print("using default RFS_CORE_HOST")
        RFS_CORE_HOST = "127.0.0.1"
        os.environ["RFS_CORE_HOST"] = RFS_CORE_HOST
    return RFS_CORE_HOST
def get_core_port():
    RFS_CORE_PORT = os.environ.get("RFS_CORE_PORT")
    if RFS_CORE_PORT is None:
        print("using default RFS_CORE_PORT")
        RFS_CORE_PORT = 50000
        os.environ["RFS_CORE_PORT"] = str(RFS_CORE_PORT)
    else:
        RFS_CORE_PORT = int(RFS_CORE_PORT)
    return RFS_CORE_PORT

def get_current_device_host():
    return socket.gethostname()
def get_current_device_ip():
    return socket.gethostbyname(socket.gethostname())



def is_core_running():

    # try:
    #     req=requests.get(f"http://{RFS.get_core_host()}:{RFS.get_core_port()}/test")
    #     if req.status_code==200:
    #         return True
    #     else:
    #         return False
    # except ConnectionError as e:
    #     return False
    # except requests.exceptions.ConnectionError as e:
    #     return False
    return is_port_in_use(obeyon_rfs.get_core_host(),obeyon_rfs.get_core_port())
    

def generate_random_port(ip_address):
    while True:
        port = random.randint(1024, 65535)
        if not is_port_in_use(ip_address, port):
            return port

def is_port_in_use(ip_address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((ip_address, port))
        except OSError:
            return True  # Port is in use
        else:
            return False  # Port is available
        
def sleep(t:float):
    if obeyon_rfs.is_core_running()==False:
        raise ConnectionError("RFS core is not available")
    time.sleep(t)

def sleep_forever():
    while True:
        sleep(1)


def generate_random_id():
    return random.randint(0, 1000000000)