import logging
import obeyon_rfs as orfs
from obeyon_rfs.inner_system.tcp_socket.SocketBase import ServerSocket, ClientSocket
import obeyon_rfs.inner_system.tcp_socket.SocketTypeORFSLogging as orfs_logging_type



class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    WHITE = '\033[97m'
    BOLD_RED = "\x1b[31;1m"


class _SocketHandler(logging.Handler):
    def __init__(self, server_host:str, server_port:int, name:str):
        super().__init__()
        self.name = name
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = ServerSocket(server_host, server_port)
    def emit(self, record):
        msg = self.format(record).encode()
        self.client.renew_socket()
        self.client.send_model(
            orfs_logging_type.Socket_Request(
                request_type=orfs_logging_type.Socket_RequestType.DIRECT_FORWARD_LOG,
                request_name=self.name,
                request_content=\
                    orfs_logging_type.Socket_RequestContent(
                        log=msg.decode()
                    ),
                request_from=\
                    orfs_logging_type.Socket_RequestFrom(
                        request_from_host=self.client.get_host_port()[0],
                        request_from_port=self.client.get_host_port()[1]
                    )
            )
        )



def log_config(name:str, log_container_server_host:str, log_container_server_port:int):
    logging.basicConfig(
        level=logging.DEBUG, 
        # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        format='%(message)s',
        handlers=[
            _SocketHandler(
                name,
                log_container_server_host,
                log_container_server_port,
            )
        ]
    )

def log_debug(msg):
    logging.debug(Color.GREEN+msg+Color.END)
def log_info(msg):
    logging.info(Color.WHITE+msg+Color.END)
def log_warn(msg):
    logging.warn(Color.YELLOW+msg+Color.END)
def log_error(msg):
    logging.error(Color.RED+msg+Color.END)
def log_critical(msg):
    logging.critical(Color.BOLD_RED+msg+Color.END)