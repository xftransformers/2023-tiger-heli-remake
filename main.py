x = 0
y = 0
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'

import pgzrun
from typing import List, Tuple
from pgzero.builtins import *
from bomb import Bomb
from tank import Tank, TANK_ANIM_FRAME_END
from bullet import Bullet
from helicopter import Helicopter
from os import path, listdir, getcwd
from math import ceil
from random import choice, random
from json import load, JSONDecodeError
from time import time

background_instances = []
place_medpack_next_tile: bool = False
medpack_instance = Actor("medpack", (0, 0))
medpack_instance.is_active = False


def calculate_bomb_dirs() -> Tuple[List[Tuple[float, float]], List[Bomb]]:
    _dirs = []
    _bombs = []

    for x in [-1, -.5, 0, .5, 1]:
        for y in [-1, -.5, 0, .5, 1]:
            _dirs.append((float(x), float(y)))

            bomb = Bomb(shooter_id=heli.__hash__())

            _bombs.append(bomb)

    return _dirs, _bombs


def get_background_list() -> List[dict]:
    _background_list = []
    for file in listdir(path.join(getcwd(), "background")):
        if not file.endswith(".json"):
            print(f"[INFO] background/{file} appears to be an invalid background file.")
            continue

        with open(f"background/{file}") as file:
            try:
                background_info: dict = load(file)
                assert background_info.__contains__("image") and isinstance(background_info["image"], str)
                assert background_info.__contains__("tank-pos") and isinstance(background_info["tank-pos"], list)
            except JSONDecodeError as e:
                print(f"[ERROR] background/{file} failed to decode: {e}")
            except AssertionError as e:
                print(f"[ERROR] background/{file} incorrectly formatted: {e}")
            else:
                _background_list.append(background_info)

    return _background_list


def setup_new_background(y: int, new_background: dict = None) -> None:
    global background_instances, tanks, place_medpack_next_tile

    if new_background is None:
        new_background = choice(backgrounds)

    instance = Actor(image=new_background['image'], anchor=("left", "bottom"), center=(WIDTH // 2, y))
    y = instance.y
    background_instances.append(instance)

    for tank_pos in new_background["tank-pos"]:
        # not every tile should have 2 tanks
        if random() > TANK_SPAWN_CHANCE:
            continue

        tx, ty = tank_pos.get("x"), tank_pos.get("y")

        if tx is None or ty is None:
            raise ValueError(f"Background is badly formatted: {new_background=}")

        new_tank = Tank(pos=(tx, ty + y - INSTANCES_HEIGHT), parent=instance)
        tanks.append(new_tank)

    if place_medpack_next_tile:
        print(f"Attempting medpack spawn...")
        if new_background.get("medpack-pos") is not None:
            medpack_pos = new_background.get("medpack-pos")

            mx, my = medpack_pos.get("x"), medpack_pos.get("y")

            assert mx is not None
            assert my is not None

            medpack_instance.pos = (mx, my + y - INSTANCES_HEIGHT)
            medpack_instance.is_active = True

            print(f"Medpack spawned at {medpack_pos.get('x')}, {medpack_pos.get('y')}")
            place_medpack_next_tile = False


def setup_backgrounds() -> List[dict]:
    global background_instances
    background_details = get_background_list()

    num_background_instances_req = ceil(HEIGHT / INSTANCES_HEIGHT) + 1

    for i in range(num_background_instances_req):
        chosen_background = choice(background_details)
        setup_new_background(INSTANCES_HEIGHT * i, chosen_background)

    return background_details


def end_game() -> None:
    global game_active

    game_active = False


WIDTH, HEIGHT = 640, 750
INSTANCES_HEIGHT = 480
BULLET_SPEED = 5
BACKGROUND_SPEED = 2
TANK_SPAWN_CHANCE = 0.75
BOMB_USAGE_TIME_SPACE = 10

count = 0
heli = Helicopter((WIDTH // 2, HEIGHT // 2), end_game)
bomb_active = False
bomb_dirs, bombs = calculate_bomb_dirs()
last_bomb_use_time = 0

tanks: List[Tank] = []
bullets: List[Bullet] = []

backgrounds = setup_backgrounds()
# print("\n".join(list([f"{n.image} - {n.y}" for n in background_instances])))

score: float = 0

game_active = True
status_text = ""


def bombs_ready_to_deploy() -> bool:
    return time() - last_bomb_use_time >= BOMB_USAGE_TIME_SPACE


def draw() -> None:
    for inst in background_instances:
        inst.draw()

    screen.blit(f"helishadow{count % 2 + 1}", (heli.x + 10, heli.y + 10))

    if medpack_instance.is_active:
        medpack_instance.draw()

    for tank in tanks:
        if tank.animation_frame < TANK_ANIM_FRAME_END:
            tank.draw()

    if bomb_active:
        for bomb in bombs:
            bomb.draw()

    for bullet in bullets:
        bullet.draw()

    heli.draw()

    if not game_active:
        screen.draw.text("GAME OVER", midbottom=(WIDTH // 2, HEIGHT // 2 - 5), fontname="press-start", fontsize=48,
                         color="red", owidth=2, ocolor="white")
        screen.draw.text(f"SCORE: {str(int(score)).zfill(6)}", midtop=(WIDTH // 2, HEIGHT // 2 + 5),
                         fontname="press-start", color="gold", owidth=2)
        return

    screen.draw.text(f"SCORE: {str(int(score)).zfill(6)}", topleft=(5, 5), color="gold", fontname="press-start")
    screen.draw.text(f"{str(heli.health).zfill(2)}HP", topright=(WIDTH - 5, 5), color="red", fontname="press-start")

    time_since_bomb_usage = time() - last_bomb_use_time
    bomb_text = "BOMBS ACTIVE" if bomb_active else \
        "BOMBS READY" if bombs_ready_to_deploy() else f"BOMBS READY IN {str(round(10 - time_since_bomb_usage, 1)).zfill(2)}s"

    screen.draw.text(bomb_text, bottomleft=(5, HEIGHT - 5), color="white", fontname="press-start")


def update() -> None:
    global count, bomb_active, score, last_bomb_use_time, place_medpack_next_tile

    if keyboard.escape:
        quit(0)

    if not game_active:
        return

    heli.update_with_inputs(keyboard.left or keyboard.a, keyboard.right or keyboard.d, keyboard.up or keyboard.w,
                            keyboard.down or keyboard.s, count)

    if keyboard.space:
        fire_bomb()

    for i, tank in enumerate(tanks):
        tank.update(BACKGROUND_SPEED)

        if tank.can_shoot_bullet:
            bullets.append(tank.spawn_bullet(heli.pos))

        if tank.top > HEIGHT:
            tanks.remove(tank)

    if bomb_active:
        for i, bomb in enumerate(bombs):
            bomb.update()

            if bomb.damage_active:
                for tank in tanks:
                    if tank.check_and_do_bomb_impact(bomb):
                        score += 120

            if not bomb.is_active:
                bomb_active = False
                last_bomb_use_time = time()

    for i, bullet in enumerate(bullets):
        bullet.update()

        x, y = bullet.pos

        if not (-16 < x < WIDTH + 16 and -16 < y < HEIGHT + 16):
            bullets.remove(bullet)

        if not bullet.active:
            continue

        for tank in tanks:
            if not tank.can_be_damaged:
                continue

            if tank.check_and_do_bullet_impact(bullet):
                score += 100 if tank.health <= 0 else 10

        heli.check_and_do_bullet_impact(bullet)

    if medpack_instance.is_active:
        if medpack_instance.colliderect(heli):
            heli.health += 10
            medpack_instance.is_active = False

        if medpack_instance.top > HEIGHT:
            medpack_instance.is_active = False

        medpack_instance.y += BACKGROUND_SPEED

    max_h: Actor = None
    min_h: Actor = None

    for instance in background_instances:
        instance.y += BACKGROUND_SPEED

        if max_h is None or instance.y > max_h.y:
            max_h = instance

        if min_h is None or instance.y < min_h.y:
            min_h = instance

    if max_h.y > (HEIGHT + INSTANCES_HEIGHT):
        background_instances.remove(max_h)

        tanks_to_remove = []
        for tank in tanks:
            if tank.parent == max_h:
                tanks_to_remove.append(tank)

        for tank in tanks_to_remove:
            tanks.remove(tank)

        setup_new_background(min_h.y - INSTANCES_HEIGHT * 1.5)

    count += 1

    if score // 500 != (score + .2) // 500:
        place_medpack_next_tile = True
        print(f"Medpack authorized.")

    score += .2


def fire_bomb() -> None:
    global bomb_active

    if bomb_active or not bombs_ready_to_deploy():
        return

    bomb_active = True
    sounds.launch.play()

    for i, bomb in enumerate(bombs):
        bomb.shooter_id = heli.__hash__()
        bomb.fire_bomb(heli.pos, bomb_dirs[i])


def on_mouse_down(pos: Tuple[float, float], button: mouse) -> None:
    bullet = Bullet.from_angle_calc(heli.pos, pos, heli)

    bullets.append(bullet)


pgzrun.go()
