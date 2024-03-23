from typing import List, Tuple


class LaunchInstruction():
    def __init__(self, cell:Tuple[int,int]):
        self.cell=cell
class LaunchCore(LaunchInstruction):
    def __init__(self,
                 name:str=None,
                 core_host:str=None,
                 core_port:int=None,
                 cell:Tuple[int,int]=None):
        self.name = name
        self.core_host = core_host
        self.core_port = core_port
        self.cell = cell
class ConnectToCore(LaunchInstruction):
    def __init__(self,
                 name:str=None,
                 core_host:str=None,
                 core_port:int=None,
                 cell:Tuple[int,int]=None):
        self.name = name
        self.core_host = core_host
        self.core_port = core_port
        self.cell = cell
class LaunchNode(LaunchInstruction):
    def __init__(self,package,executable,cell):
        self.package = package
        self.executable = executable
        self.cell = cell
class LaunchConfig():
    def __init__(self,grid_cells:Tuple[int,int],instructions:List[LaunchInstruction]):
        self.grid_cells = grid_cells
        self.instructions = instructions

        self._core_host:str = None
        self._core_port:int = None
    def run(self):
        for instruction in self.instructions:
            if isinstance(instruction,LaunchCore):
                pass
            if isinstance(instruction,ConnectToCore):
                pass
            if isinstance(instruction,LaunchNode):
                pass
        pass