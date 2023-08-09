#!/usr/bin/env python3

from flask import Blueprint
from .. import db
import json
from .util import error, success, check_request, generate_rolls, generate_rolls_uid

router = Blueprint('dice', __name__)


@router.route('/api/dice/throw', methods=['POST'])
def _api_dice_throw():
    data, req_error = check_request(
        ("game_uuid", "username", "faces", "number", "uid", "hide"))
    if req_error:
        return req_error
    try:
        game = db.query_db(
            'select * from game where uuid = ?', (data['game_uuid'],), one=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    if not game:
        return error(data['uid'], "game doesn't exist")
    game = dict(game)
    number, faces = int(data['number']), int(data['faces'])
    rolls = generate_rolls(number, faces)
    rolls_json = json.loads(game['rolls'])
    rolls_json['rolls'].append({
        'uid': str(generate_rolls_uid()),
        'username': data['username'],
        'rolls': rolls,
        'formatted_dice': f'{number}d{faces}',
        'hide': data['hide'],
    })
    try:
        db.query_db(
            'update game set rolls = ? where uuid = ?', (json.dumps(rolls_json), data['game_uuid']), commit=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], 'game exists')
