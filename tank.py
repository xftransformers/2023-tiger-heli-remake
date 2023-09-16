from pgzero.builtins import *
from bullet import Bullet
from typing import Tuple
from damageable import DamageableActor
from random import randint

TANK_ANIM_FRAME_END = 10
TANK_SHOOT_RATE = 1

FRAMES_PER_BULLET = (1000 / TANK_SHOOT_RATE) // 16


class Tank(DamageableActor):
    def __init__(self, pos: Tuple[int, int], parent: Actor) -> None:
        super(Tank, self).__init__("tank0", pos)
        self.animation_frame = 0
        self.health = 3
        self.frames_since_bullet = 0
        self.parent = parent

    def update(self, y_change: int) -> None:
        self.y += y_change

        if self.y > 850:
            self.animation_frame = 0

        if 0 < self.animation_frame < 10:
            self.animation_frame += .2

        self.image = f"tank{int(self.animation_frame)}"

        self.frames_since_bullet += 1

    @property
    def can_shoot_bullet(self):
        return self.frames_since_bullet >= FRAMES_PER_BULLET

    def spawn_bullet(self, target: Tuple[int, int]) -> Bullet:
        self.frames_since_bullet = 0

        return Bullet.from_angle_calc(self.pos, target, self, angle_change=randint(-5, 5))

    @property
    def can_be_damaged(self):
        return self.animation_frame == 0

    def die(self):
        self.animation_frame = 1
        sounds.explosion.play()

    def inflict_damage(self, damage: float = 1) -> None:
        if not self.can_be_damaged:
            return

        return super().inflict_damage(damage)

