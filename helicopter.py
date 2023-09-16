from pgzero.builtins import *
from utils import clamp
from damageable import DamageableActor
from bullet import Bullet
from typing import Callable

SPEED = 2


class Helicopter(DamageableActor):
    def __init__(self, pos, callback: Callable[[], None]):
        super(Helicopter, self).__init__("heli1", pos)
        self.health = 25
        self.callback = callback

    def update_with_inputs(self, horizontal_left: bool, horizontal_right: bool,
                           vertical_up: bool, vertical_down: bool,
                           count: int) -> None:
        if horizontal_left:
            self.x -= SPEED

        if horizontal_right:
            self.x += SPEED

        if vertical_up:
            self.y -= SPEED

        if vertical_down:
            self.y += SPEED

        self.x = clamp(self.x, 50, 550)
        self.y = clamp(self.y, 50, 750)

        self.image = f"heli{count % 2 + 1}"

    @property
    def can_be_damaged(self) -> bool:
        return self.health > 0

    def check_and_do_bullet_impact(self, bullet: Bullet) -> bool:
        if bullet.colliderect(self) and bullet.shooter_id != self.__hash__() and bullet.active:
            self.inflict_damage(1)
            bullet.active = False
            return True

        return False

    def die(self):
        self.callback()





