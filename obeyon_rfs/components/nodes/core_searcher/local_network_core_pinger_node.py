
from typing import TYPE_CHECKING, List, NoReturn, Tuple
import uuid

from obeyon_rfs.components import ORFS_Message, ORFS_MessageType
import dns.resolver
# import aioping
import asyncio
from asyncio import StreamReader, StreamWriter
import sys
import obeyon_rfs
from obeyon_rfs.components.nodes import Node

class LocalNetworkCorePingerNode(Node):
    """
        The node that pings the core node in the local network by broadcasting
    """
    def __init__(self,domain_name="",search_timeout=4.0,search_on_port=7134,subnet_mask="255.255.255.0"):
        super().__init__(
            node_name="temp_node"+uuid.uuid4().hex,
            receiver_host=obeyon_rfs.get_local_ip_address(),
            receiver_port=0,
            domain_name=domain_name,
        )
        self.search_timeout=search_timeout
        self.search_on_port=search_on_port
        self.subnet_mask=subnet_mask
        self.ping_timer=self.create_timer(2.0,self.broadcast_ping)
        self.pong_cores:List[ORFS_Message]=[]


        self.additional_handle_client_callbacks.append(self.__additional_handle_client)

    async def broadcast_ping(self):
        # obeyon_rfs.log_info(self.pong_cores)
        # obeyon_rfs.log_info("Broadcasting ping...")
        # obeyon_rfs.log_info("Waiting node receiver server...")
        while True:
            await asyncio.sleep(0)
            if self.receiver_port!=0:
                break
        # obeyon_rfs.log_info("Searching accessible sockets...")
        current_ip=obeyon_rfs.get_local_ip_address()
        dns_servers = dns.resolver.Resolver().nameservers
        # print(dns_servers)
        async def ping_core(ip_address,port):
            try:
                # obeyon_rfs.log_info(f"Testing {port} port on {ip_address}...")
                reader,writer = await asyncio.wait_for(asyncio.open_connection(ip_address,port),timeout=self.search_timeout)
                # obeyon_rfs.log_info(f"Connected to {ip_address}:{port}")
                model=ORFS_Message(
                    message_type=ORFS_MessageType.BROADCAST_CORE_PING,
                    message_name='ping',
                    message_content={},
                    node_name=self.node_name,
                    node_receiver_host=self.receiver_host,
                    node_receiver_port=self.receiver_port,
                    domain_name=self.domain_name
                )
                # print("Sending:",model)
                b64_model=model.base64_encode()
                # print("Sending:",b64_model)
                writer.write(b64_model)
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except ConnectionRefusedError as e:
                # obeyon_rfs.log_info(f"Connection refused on {ip_address}:{port}")
                pass
            except TimeoutError as e:
                # obeyon_rfs.log_info(f"Timeout on {ip_address}:{port}")
                pass
            except OSError as e:
                if e.errno==111: #Basically connection refused I guess
                    # obeyon_rfs.log_info(f"Connection refused OS on {ip_address}:{port}")
                    pass
                else:
                    raise e
        tasks=[]
        for i in range(0,255):
            ip_address_digits=[]
            for v,mask in zip(current_ip.split('.'),self.subnet_mask.split('.')):
                if mask=='0':
                    ip_address_digits.append(str(i))
                elif mask=='255':
                    ip_address_digits.append(v)
            ip_address = '.'.join(ip_address_digits)
            if ip_address not in dns_servers:
                tasks.append(ping_core(ip_address,self.search_on_port))
        tasks.append(ping_core('127.0.0.1',self.search_on_port))
        tasks.append(ping_core('localhost',self.search_on_port))
        await asyncio.gather(*tasks)

    async def __additional_handle_client(self,model:ORFS_Message,reader:StreamReader,writer:StreamWriter):
        if model.message_type==ORFS_MessageType.CORE_PONG:
            #no need to check domain name
            obeyon_rfs.log_info("Pong from",model.node_name,model.node_receiver_host,model.node_receiver_port)
            self.pong_cores.append(model)
    
    def return_core_host_port(self)->Tuple[str,int]:
        cores=map(lambda x:(x.node_receiver_host,x.node_receiver_port),self.pong_cores)
        cores=list(set(cores))
        if len(cores)==0:
            sys.exit('No CoreNode found.')
        if len(cores)>1:
            sys.exit('Multiple CoreNode found.')
        core=cores[0]
        return core
    
    def start_as_main(self,exit_time:float=10.0) -> NoReturn | None:
        super().start_as_main(exit_time=exit_time)
        

    # async def _search_host_port(self)->Tuple[str,int]:
    #     obeyon_rfs.log_info("Searching CoreNode...")
    #     obeyon_rfs.log_info("Waiting node receiver server...")
    #     while True:
    #         await asyncio.sleep(0)
    #         if self.receiver_port!=0:
    #             break
    #     obeyon_rfs.log_info("Searching accessible sockets...")
    #     current_ip=obeyon_rfs.get_local_ip_address()
    #     dns_servers = dns.resolver.Resolver().nameservers
    #     async def ping_core_append(ip_address,port):
    #         try:
    #             print(f"Testing {port} port on {ip_address}...")
    #             reader,writer = await asyncio.wait_for(asyncio.open_connection(ip_address,port),timeout=self.search_timeout)
    #             writer.write(ORFS_Message(
    #                 message_type=ORFS_MessageType.CORE_PING,
    #                 message_name='ping',
    #                 message_content={},
    #                 node_name=self.node_name,
    #                 node_receiver_host=self.receiver_host,
    #                 node_receiver_port=self.receiver_port
    #             ).base64_encode())
    #             await writer.drain()
    #             data = await asyncio.wait_for(reader.read(2048),timeout=self.search_timeout)
    #             model = ORFS_Message.base64_decode(data)
    #             if model is not None:
    #                 if model.message_type==ORFS_MessageType.CORE_PONG:
    #                     obeyon_rfs.log_info(f"CoreNode found on {ip_address}:{port}")
    #                     return (ip_address,port)
    #             writer.close()
    #             await writer.wait_closed()
    #         except ConnectionRefusedError as e:
    #             pass
    #         except TimeoutError as e:
    #             pass
    #         except OSError as e:
    #             if e.errno==111: #Basically connection refused I guess
    #                 pass
    #         return None
    #     tasks=[]
    #     for i in range(1,255):
    #         ip_address_digits=[]
    #         for v,mask in zip(current_ip.split('.'),self.subnet_mask.split('.')):
    #             if mask=='0':
    #                 ip_address_digits.append(str(i))
    #             elif mask=='255':
    #                 ip_address_digits.append(v)
    #         ip_address = '.'.join(ip_address_digits)
    #         if ip_address not in dns_servers:
    #             tasks.append(ping_core_append(ip_address,self.search_on_port))
    #     tasks.append(ping_core_append('127.0.0.1',self.search_on_port))
    #     tasks.append(ping_core_append('localhost',self.search_on_port))
    #     results = await asyncio.gather(*tasks)
    #     results = [r for r in results if r is not None]
    #     obeyon_rfs.log_info("Connectable :",*results)
    #     if len(results)==0:
    #         sys.exit('CoreNode connection lost')
    #     if len(results)>1:
    #         sys.exit('Multiple CoreNode found.')
    #     return results[0]
    # def search_host_port(self)->Tuple[str,int]:
    #     return asyncio.run(self._search_host_port())
    