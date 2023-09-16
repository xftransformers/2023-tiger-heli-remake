x = 0
y = 0
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'

import pygame
from pgzero.builtins import *
import pgzrun
from spriteinstance import Instance
from typing import Tuple, List, Dict
from os import listdir, getcwd, path
from pygame.image import save, load_extended
from pygame.mouse import get_pos
from string import printable
from uuid import uuid4
from json import dump


def get_sets() -> Dict[str, int]:
    sets = dict()

    path_ = path.join(getcwd(), "images", "newtiles")
    for file in listdir(path_):
        file_set = file.split("--")[0]
        sets[file_set] = sets.setdefault(file_set, 0) + 1

    return dict(sets)


tile_sets_sprites = get_sets()
tile_sets = tuple(tile_sets_sprites.keys())


def get_curr_tile_path() -> str:
    global tile_sets_sprites
    return f"newtiles/{tile_sets[curr_set_index]}--{curr_tile_num}.png"


def snap_to_grid(location: Tuple[int, int], grid_size: float = 16) -> tuple[int, int]:
    x, y = location
    return int(round(x / grid_size) * grid_size), int(round(y / grid_size) * grid_size)


def get_polarity(num: float) -> int:
    return 1 if num >= 0 else -1


def get_drag_direction(start: Tuple[int, int], end: Tuple[int, int]):
    start_x, start_y = snap_to_grid(start)
    end_x, end_y = snap_to_grid(end)

    dx, dy = end_x - start_x, end_y - start_y
    diff = abs(dx) - abs(dy)

    if abs(diff) < (abs(dx) + abs(dy)) // 2:
        return get_polarity(dx), get_polarity(dy)

    if diff > 0:
        return get_polarity(dx), 0

    return 0, get_polarity(dy)


WIDTH, HEIGHT = 640, 480

curr_tile_num = 0
curr_set_index = 0
curr_tile_actor = Actor(get_curr_tile_path(), topleft=(0, 0))
instances: List[Instance] = [Instance(get_curr_tile_path(), pos=(WIDTH // 2, HEIGHT // 2))]
dragged_tile_actors = []
background_sprite: Instance = None

is_saving = False
is_dragging = False
drag_start_pos = (0, 0)
dragging_instances: List[Instance] = []

setup_complete = False
file_loc_input = ""

placing_special = False
placing_tank = False
placing_medpack = False
tanks: List[Instance] = []
medpack_instance: Instance = None  # Only 1 medpack per background tile

IMG_ID = uuid4()


def draw() -> None:
    global is_saving, dragging_instances

    screen.clear()

    if not setup_complete:
        screen.draw.text("Enter file location (absolute or relative to 'images' directory) to load file", fontsize=24,
                         topleft=(0, 0))
        screen.draw.text(file_loc_input, fontsize=24, topleft=(0, 20))

        return

    if background_sprite is None:
        screen.fill((100, 100, 100))
    else:
        background_sprite.draw()

    for instance in instances:
        instance.draw()

    if is_saving:  # tanks won't be drawn because screen was cleared, and called before tanks drawn
        save(screen.surface, f"images/background/{IMG_ID}.png")

        tank_pos_list = list([{"x": int(n.x), "y": int(n.y)} for n in tanks])
        medpack_pos = dict() if medpack_instance is None else {"x": medpack_instance.x, "y": medpack_instance.y}

        with open(path.join(getcwd(), "background", f"{IMG_ID}.json"), "w") as file:
            dump({
                "image": f"background/{IMG_ID}.png",
                "tank-pos":  tank_pos_list,
                "medpack-pos": medpack_pos
            }, file, indent=4)

        is_saving = False
        return

    for tank in tanks:
        tank.draw()

    if medpack_instance is not None:
        medpack_instance.draw()


    if is_dragging:
        dragging_instances = generate_dragged_blocks(drag_start_pos, get_pos(), dragging_instances)
        for instance in dragging_instances:
            if instance.in_use:
                instance.draw()

        return

    curr_tile_actor.draw()

    screen.draw.text(tile_sets[curr_set_index], bottomright=(WIDTH, HEIGHT))


def update(dt: float) -> None:
    global setup_complete, background_sprite, curr_tile_actor

    angle = curr_tile_actor.angle
    new_image = get_curr_tile_path() if not placing_special else \
        "tank0" if placing_tank else "medpack"
    curr_tile_actor.image = new_image
    curr_tile_actor.angle = angle


def on_mouse_down(pos: Tuple[int, int], button: mouse) -> None:
    global is_saving, is_dragging, medpack_instance

    if button == mouse.LEFT:
        if placing_tank:
            tanks.append(Instance("tank0", snap_to_grid(pos), curr_tile_actor.angle))
            return

        if placing_medpack:
            medpack_instance = Instance("medpack", snap_to_grid(pos), 0)
            return

        if is_dragging:
            for instance in [n for n in dragging_instances if n.in_use]:
                instances.append(instance)
                dragging_instances.remove(instance)

            is_dragging = False
            return

        new_instance = Instance(get_curr_tile_path(), snap_to_grid(pos), curr_tile_actor.angle)
        instances.append(new_instance)
        return

    if button == mouse.RIGHT:
        if is_dragging:
            disable_dragging()
            return

        pos = snap_to_grid(pos)

        for instance in instances[::-1]:
            if instance.pos == pos and not instance.is_loaded_img:
                instances.remove(instance)
                break

        return

    if button == mouse.WHEEL_UP:
        alter_tile_selected(1)
        return

    if button == mouse.WHEEL_DOWN:
        alter_tile_selected(-1)
        return

    if button == mouse.MIDDLE:
        is_saving = True


def on_mouse_move(pos: Tuple[int, int]) -> None:
    curr_tile_actor.pos = snap_to_grid(pos)


def alter_set(change: int) -> None:
    global curr_set_index, curr_tile_num

    curr_set_index += change
    curr_set_index %= len(tile_sets)

    curr_tile_num = 0


def alter_tile_selected(change: int) -> None:
    global curr_tile_num

    curr_tile_num += change
    curr_tile_num %= tile_sets_sprites[tile_sets[curr_set_index]]

    curr_tile_actor.angle = 0


def on_key_down(key: keyboard, mod: int) -> None:
    global curr_tile_num, curr_set_index, is_dragging, drag_start_pos, setup_complete, file_loc_input, \
        background_sprite, placing_tank, placing_medpack, placing_special

    if keyboard.ESCAPE and len(instances) in (0, 1):
        quit(0)

    if not setup_complete:
        if keyboard.RETURN:
            try:
                assert file_loc_input.strip() != ""
                background_sprite = Instance(file_loc_input, pos=(WIDTH // 2, HEIGHT // 2), is_loaded_img=True)
            except AssertionError:
                # no file, so just continue
                setup_complete = True  # use blank canvas
            except (FileNotFoundError, KeyError) as _:
                ...
            except pygame.error:
                raise ValueError(f"File {file_loc_input} is in an invalid image format.")
            else:
                setup_complete = True

            return

        if keyboard.BACKSPACE:
            file_loc_input = file_loc_input[:len(file_loc_input) - 1]
            return

        try:
            str_pressed = chr(key)

            if mod in [keymods.LSHIFT, keymods.RSHIFT, keymods.SHIFT, keymods.CAPS]:
                str_pressed = str_pressed.upper()

            if str_pressed in printable:
                file_loc_input += str_pressed
        except ValueError as _:
            ...

        return

    if keyboard.Q:
        if is_dragging or placing_special:
            return

        alter_tile_selected(-1)

    if keyboard.E:
        if is_dragging or placing_special:
            return

        alter_tile_selected(1)

    if keyboard.Z:
        if is_dragging:
            return

        alter_set(-1)

    if keyboard.C:
        if is_dragging:
            return

        alter_set(1)

    if keyboard.R:
        if is_dragging:
            return

        curr_tile_actor.angle += 90

    if keyboard.F:
        if placing_special:
            return

        is_dragging = not is_dragging

        if not is_dragging:
            disable_dragging()
            return

        drag_start_pos = get_pos()

    if keyboard.T:
        is_dragging = False
        placing_tank = not placing_tank
        placing_medpack = False
        placing_special = placing_tank

    if keyboard.M:
        is_dragging = False
        placing_tank = False
        placing_medpack = not placing_medpack
        placing_special = placing_medpack


def disable_dragging() -> None:
    global is_dragging, dragging_instances

    for dragging_instance in dragging_instances:
        dragging_instance.in_use = False

    is_dragging = False


def generate_dragged_blocks(start: Tuple[int, int], end: Tuple[int, int], _instances: List[Instance]) -> List[Instance]:
    if _instances is None:
        _instances = []

    start, end = snap_to_grid(start), snap_to_grid(end)

    direction_vec = get_drag_direction(start, end)

    dx, dy = end[0] - start[0], end[1] - start[1]

    if dx % 16 != 0 or dy % 16 != 0:
        print(f"dx ({dx}) or dy ({dy}) did not snap to grid correctly.")

    if direction_vec[0] == 0:
        num_required = abs(dy) // 16 + 1
    else:
        num_required = abs(dx) // 16 + 1

    i = 0
    start_x, start_y = start
    dir_x, dir_y = direction_vec

    # print(f"{num_required=}; {direction_vec=}; {start=}; {end=}")

    for instance in _instances:
        if i >= num_required:
            instance.in_use = False
            i += 1
            continue

        instance.image = curr_tile_actor.image
        instance.angle = curr_tile_actor.angle

        instance.pos = (start_x + dir_x * 16 * i), (start_y + dir_y * 16 * i)
        instance.in_use = True
        i += 1

    if i >= num_required:
        return _instances

    for instance_num in range(i, int(num_required + 1)):
        pos = (start_x + dir_x * 16 * instance_num), (start_y + dir_y * 16 * instance_num)
        new_instance = Instance(curr_tile_actor.image, pos, curr_tile_actor.angle)

        _instances.append(new_instance)

    return _instances


pgzrun.go()
