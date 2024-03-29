
from typing import TYPE_CHECKING, List, Tuple

from obeyon_rfs.components import ORFS_Message, ORFS_MessageType
if TYPE_CHECKING:
    import dns
    import socket
    import aioping
    import asyncio
    import sys
    import obeyon_rfs
    from obeyon_rfs.components.nodes import Node

class TCPCoreSearcherNode(Node):
    def __init__(self,search_timeout=2.0,search_on_port=7134,subnet_mask="255.255.255.0"):
        super().__init__("temp_node")
        self.search_timeout=search_timeout
        self.search_on_port=search_on_port
        self.subnet_mask=subnet_mask
        
    async def all_ip_address(self)->List[str]:
        current_ip=socket.gethostbyname(socket.gethostname())
        dns_servers = dns.resolver.Resolver().nameservers
        connectable_ip=[]
        tasks = []
        async def ping_append(ip_address):
            try:
                await aioping.ping(ip_address,timeout=1)
                connectable_ip.append(ip_address)
            except TimeoutError as e:
                pass
        for i in range(1,255):
            ip_address_digits=[]
            for v,mask in zip(current_ip.split('.'),self.subnet_mask.split('.')):
                if mask=='0':
                    ip_address_digits.append(str(i))
                elif mask=='255':
                    ip_address_digits.append(v)
            ip_address = '.'.join(ip_address_digits)
            if ip_address not in dns_servers:
                tasks.append(ping_append(ip_address))
        await asyncio.gather(*tasks)
        return connectable_ip
    async def _search_host_port(self)->Tuple[str,int]:
        obeyon_rfs.log_info("Searching CoreNode...")
        obeyon_rfs.log_info("Searching accessible ip address...")
        all_ip=await self.all_ip_address()
        obeyon_rfs.log_info(all_ip)
        for ip in all_ip:
            print(f"Testing {self.search_on_port} port on {ip}...")
            try:
                reader,writer = await asyncio.open_connection(ip,self.search_on_port)
            except ConnectionRefusedError as e:
                continue
            writer.write(ORFS_Message(
                message_type=ORFS_MessageType.CORE_PING,
                message_name='ping',
                message_content={},
                node_name=self.node_name,
                node_receiver_host=ip,
                node_receiver_port=self.search_on_port
            ).base64_encode())
            await writer.drain()
            data = await reader.read(2048)
            model = ORFS_Message.base64_decode(data)
            if model is not None:
                if model.message_type==ORFS_MessageType.CORE_PONG:
                    obeyon_rfs.log_info(f"CoreNode found on {ip}:{self.search_on_port}")
                    return (model.node_receiver_host,model.node_receiver_port)
            writer.close()
            await writer.wait_closed()
        sys.exit('CoreNode connection lost')
        return ('',0)
    def search_host_port(self)->Tuple[str,int]:
        return asyncio.run(self._search_host_port())