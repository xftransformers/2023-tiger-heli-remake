from pgzero.builtins import *
from typing import Tuple

BOMB_SPEED = 5

DESTROY_BOMB_ANIMATION_FRAME = 40
DAMAGE_ACTIVATE_START_FRAME = 30


class Bomb(Actor):
    def __init__(self, shooter_id: int) -> None:
        super(Bomb, self).__init__('bomb1', center=(0, 0))
        self.animation_frame = 0
        self.shooter_id = shooter_id

        self.direction = (.0, .0)

    def update(self):
        self.y += 1

        dir_x, dir_y = self.direction
        self.x += dir_x * BOMB_SPEED
        self.y += dir_y * BOMB_SPEED

        self.animation_frame += 1

        if self.damage_active:
            self.image = f"bomb{self.animation_frame - DAMAGE_ACTIVATE_START_FRAME}"

    @property
    def damage_active(self) -> bool:
        return self.animation_frame > DAMAGE_ACTIVATE_START_FRAME

    @property
    def is_active(self) -> bool:
        return self.animation_frame != DESTROY_BOMB_ANIMATION_FRAME

    def fire_bomb(self, position: Tuple[float, float], direction: Tuple[float, float]):
        self.animation_frame = 1
        self.pos = position
        self.image = "bomb1"

        self.direction = direction



