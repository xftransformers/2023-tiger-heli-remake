from pgzero.builtins import *
from damageable import DamageableActor
from typing import Tuple
from math import sin, cos, degrees

SPEED = 2


class Missile(DamageableActor):
    def __init__(self, pos: Tuple[int, int], target: DamageableActor):
        super(Missile, self).__init__("bomb2", pos)
        self.target = target
        self.dead = False

    def update(self):
        dx, dy = self.target.x - self.x, self.target.y - self.y

        angle_to_heli = self.angle_to(self.target)

        vel_x, vel_y = SPEED * sin(angle_to_heli), SPEED * cos(angle_to_heli)

        self.x -= vel_x
        self.y -= vel_y

    def draw(self):
        if self.dead:
            return

        super(Missile, self).draw()

    def die(self):
        self.dead = True

    @property
    def can_be_damaged(self) -> bool:
        return not self.dead


