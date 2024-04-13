
from typing import TYPE_CHECKING, List, Tuple

from obeyon_rfs.components import ORFS_Message, ORFS_MessageType
import dns.resolver
import socket
# import aioping
import asyncio
import sys
import obeyon_rfs
from obeyon_rfs.components.nodes import Node

class LocalNetworkCoreSearcherNode(Node):
    def __init__(self,search_timeout=4.0,search_on_port=7134,subnet_mask="255.255.255.0"):
        super().__init__(
            node_name="temp_node",
            receiver_host=obeyon_rfs.get_local_ip_address(),
            receiver_port=0
        )
        self.search_timeout=search_timeout
        self.search_on_port=search_on_port
        self.subnet_mask=subnet_mask

    async def _search_host_port(self)->Tuple[str,int]:
        obeyon_rfs.log_info("Searching CoreNode...")
        obeyon_rfs.log_info("Searching accessible sockets...")
        current_ip=socket.gethostbyname(socket.gethostname())
        dns_servers = dns.resolver.Resolver().nameservers
        async def ping_core_append(ip_address,port):
            try:
                print(f"Testing {port} port on {ip_address}...")
                reader,writer = await asyncio.wait_for(asyncio.open_connection(ip_address,port),timeout=self.search_timeout)
                writer.write(ORFS_Message(
                    message_type=ORFS_MessageType.CORE_PING,
                    message_name='ping',
                    message_content={},
                    node_name=self.node_name,
                    node_receiver_host=ip_address,
                    node_receiver_port=port
                ).base64_encode())
                await writer.drain()
                data = await asyncio.wait_for(reader.read(2048),timeout=self.search_timeout)
                model = ORFS_Message.base64_decode(data)
                if model is not None:
                    if model.message_type==ORFS_MessageType.CORE_PONG:
                        obeyon_rfs.log_info(f"CoreNode found on {ip_address}:{port}")
                        return (ip_address,port)
                writer.close()
                await writer.wait_closed()
            except ConnectionRefusedError as e:
                pass
            except TimeoutError as e:
                pass
            return None
        tasks=[]
        for i in range(1,255):
            ip_address_digits=[]
            for v,mask in zip(current_ip.split('.'),self.subnet_mask.split('.')):
                if mask=='0':
                    ip_address_digits.append(str(i))
                elif mask=='255':
                    ip_address_digits.append(v)
            ip_address = '.'.join(ip_address_digits)
            if ip_address not in dns_servers:
                tasks.append(ping_core_append(ip_address,self.search_on_port))
        tasks.append(ping_core_append('127.0.0.1',self.search_on_port))
        tasks.append(ping_core_append('localhost',self.search_on_port))
        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]
        obeyon_rfs.log_info("Connectable :",*results)
        if len(results)==0:
            sys.exit('CoreNode connection lost')
        if len(results)>1:
            sys.exit('Multiple CoreNode found.')
        return results[0]
    def search_host_port(self)->Tuple[str,int]:
        return asyncio.run(self._search_host_port())