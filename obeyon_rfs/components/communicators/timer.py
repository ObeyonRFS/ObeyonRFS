import asyncio
from typing import TYPE_CHECKING, Any, Callable, Coroutine
from obeyon_rfs.components import ORFS_Component, ORFS_MessageType, ORFS_Message
if TYPE_CHECKING:
    from obeyon_rfs.components.nodes import Node


class Timer(ORFS_Component):
    def __init__(self,timer_interval:float,coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None):
        super().__init__()
        self.parent:Node = None
        self.timer_interval=timer_interval
        self.coroutine_callback=coroutine_callback
    
    async def _start(self):
        while True:
            await asyncio.sleep(self.timer_interval)
            if self.coroutine_callback is not None:
                await self.coroutine_callback()
            # if self.callback is Coroutines:
            #     await self.callback()
            # elif self.callback is not None:
            #     self.callback()


    # def stop(self):
    #     pass
    # def set_interval(self,interval:float):
    #     pass
    # def set_callback(self,callback:Callable[[],None]):
    #     pass
    # def __repr__(self):
    #     return f'<Timer {self.timer_interval} {self.timer_callback}>'
    # def __str__(self):
    #     return f'<Timer {self.timer_interval} {self.timer_callback}>'