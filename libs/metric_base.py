import abc
from pathlib import Path
from typing import Union, List, Tuple

import open3d as o3d

class MetricBase(metaclass=abc.ABCMeta):
    """Base class of metrics.
    """
    def __init__(
            self,
            ref_pc: Union[str, Path],
            target_pc: Union[str, Path]
        ) -> None:
        self._ref_pc = ref_pc
        self._target_pc = target_pc
        self._has_color = o3d.io.read_point_cloud(self._ref_pc).has_colors()
        self._has_normal = o3d.io.read_point_cloud(self._ref_pc).has_normals()
        self._results = []
    
    @abc.abstractmethod
    def evaluate(self) -> str:
        return NotImplemented