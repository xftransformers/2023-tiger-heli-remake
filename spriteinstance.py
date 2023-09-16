from pgzero.builtins import *
from typing import Tuple


class Instance(Actor):
    def __init__(self, image: str, pos: Tuple[int, int], angle: float = 0, is_loaded_img: bool = False, **kwargs):
        super(Instance, self).__init__(image, center=pos, **kwargs)
        self.angle = angle
        self.in_use = True
        self.is_loaded_img = is_loaded_img



