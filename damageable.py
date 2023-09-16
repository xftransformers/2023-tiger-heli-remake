from pgzero.builtins import *
from typing import Tuple
from abc import abstractmethod, ABC
from bullet import Bullet
from bomb import Bomb


class DamageableActor(ABC, Actor):
    def __init__(self, img: str, pos: Tuple[int, int], **kwargs):
        super(DamageableActor, self).__init__(img, center=pos)
        self.health: float = 3

    def inflict_damage(self, damage: float = 1) -> None:
        self.health -= damage

        if self.health <= 0:
            self.die()

    @property
    @abstractmethod
    def can_be_damaged(self) -> bool: ...

    def check_and_do_bullet_impact(self, bullet: Bullet) -> bool:
        if self.colliderect(bullet) and bullet.shooter_id != self.__hash__():
            bullet.active = False
            self.inflict_damage(1)
            return True

        return False

    def check_and_do_bomb_impact(self, bomb: Bomb) -> bool:
        if self.colliderect(bomb) and bomb.shooter_id != self.__hash__() and self.can_be_damaged:
            self.die()

            return True

        return False

    @abstractmethod
    def die(self) -> None: ...
