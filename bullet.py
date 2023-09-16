from pgzero.builtins import *
from typing import Tuple, Self
from math import atan, sin, cos, degrees, radians

BULLET_SPEED = 5


class Bullet(Actor):
    def __init__(self, pos: Tuple[float, float], vel: Tuple[float, float], shooter_id: int, angle: int = 0) -> None:
        super(Bullet, self).__init__('bullet', center=pos)
        self.vel = vel
        self.shooter_id = shooter_id
        self.active = True
        self.angle = angle

    @staticmethod
    def from_angle_calc(pos: Tuple[float, float], target_pos: Tuple[float, float], shooter: object | int, \
                        angle_change: float = 0) -> Self:
        if not isinstance(shooter, int):
            shooter = shooter.__hash__()

        pos_x, pos_y = pos
        mouse_x, mouse_y = target_pos

        dy, dx = mouse_y - pos_y, mouse_x - pos_x

        if dx == 0:
            angle = 180 * (1 if dy >= 0 else -1)
        else:
            angle = degrees(atan(-dy / dx)) + 90

            if dx > 0:
                angle += 180

        # angle_change is to introduce slight inaccuracy in enemies firing at the player
        angle += angle_change

        vel = (-BULLET_SPEED * sin(radians(angle)), -BULLET_SPEED * cos(radians(angle)))
        return Bullet(pos, vel, shooter, angle)

    def update(self):
        vel_x, vel_y = self.vel

        self.x += vel_x
        self.y += vel_y







