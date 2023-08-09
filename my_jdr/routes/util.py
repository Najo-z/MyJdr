#!/usr/bin/env python3

import json
from flask import request


def error(uid: str, error: str = "db error", code: int = 400, **kwargs) -> tuple[str, int]:
    response = {
        'uid': uid,
        'error': error,
    }
    for k, v in kwargs.items():
        response[k] = v
    return json.dumps(response), code


def success(uid: str, ok: str = "Success.", code: int = 200, **kwargs) -> tuple[str, int]:
    response = {
        'uid': uid,
        'ok': ok,
    }
    for k, v in kwargs.items():
        response[k] = v
    return json.dumps(response), code


def check_request(required: tuple[str] = ("uid",)) -> tuple[dict | None, str | None]:
    if len(request.data) > 100000:
        print(
            f'Large request incoming with size {len(request.data)}. Ignoring.')
        return None, error("-1", "Too large request")
    data = json.loads(request.data)
    if not all((r in data for r in required)):
        print(
            f'Request with missing one of {required}.')
        return None, error(data['uid'], "Invalid format")
    return data, None
