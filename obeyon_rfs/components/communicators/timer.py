class Timer(ORFS_Component):
    def __init__(self,timer_interval:float,callback:Callable[[],None]=None,coroutine_callback:Callable[[],Coroutine[Any,Any,None]]=None):
        super().__init__()
        self.parent:AppNode|CoreNode|SerialDriverNode = None
        self.timer_interval=timer_interval
        self.callback=callback
        self.coroutine_callback=coroutine_callback
    
    async def _start(self):
        while True:
            await asyncio.sleep(self.timer_interval)
            if self.coroutine_callback is not None:
                # await self.coroutine_callback()
                asyncio.create_task(self.coroutine_callback())
            if self.callback is not None:
                self.callback()
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