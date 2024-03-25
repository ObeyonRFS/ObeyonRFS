import random
import time
from typing import Any, Dict

from pydantic import BaseModel

import os
import socket
import psutil
import requests


from obeyon_rfs.node import *
from obeyon_rfs.interface_system.event import *
from obeyon_rfs.core import *
from obeyon_rfs.interface_system.comm_type import *

__version__ = '0.0.10'
__module_dir__ = os.path.dirname(__file__)



class InitArgs(BaseModel):
    node_name:str = None
    ORFS_CORE_HOST:str = "127.0.0.1"
    ORFS_CORE_PORT:int = 50000
    log_forwarding_server_host:str = None
    log_forwarding_server_port:int = None


_init_args:InitArgs=InitArgs()

def init(args:InitArgs=None):
    global _init_args
    if args is None:
        return
    _init_args=InitArgs(**args.model_dump())


def spin_once(period_time=0.001):
    if obeyon_rfs.is_core_running()==False:
        raise ConnectionError("ObeyonRFS core is not available")
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
    
        
def sleep(t:float):
    time.sleep(t)

def sleep_forever():
    while True:
        sleep(1)


def generate_random_id():
    return random.randint(0, 1000000000)



def pydantic_validation_check(model:BaseModel, data:Dict[str,Any]):
    try:
        model(**data)
    except ValidationError as e:
        return False
    return True