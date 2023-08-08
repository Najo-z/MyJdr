#!/usr/bin/env python3

import random
import uuid


def generate_lobby_code(in_use):
    r = random.randint(1000, 9999)
    while r in in_use:
        r = random.randint(1000, 9999)
    return r


def generate_game_code():
    return uuid.uuid4()


def generate_rolls_uid():
    return uuid.uuid4()


def generate_rolls(number: int = 1, faces: tuple[int] = 10) -> list[int]:
    r = [random.randint(0, faces-1) for _ in range(number)]
    return r
