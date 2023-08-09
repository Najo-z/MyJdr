#!/usr/bin/env python3

from flask import Blueprint
from .. import db
import json
from .util import error, success, check_request

router = Blueprint('game', __name__)


@router.route('/api/game/list_one', methods=['POST'])
def _api_game_list_one():
    data, req_error = check_request(("game_uuid", 'uid'))
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
    return success(
        data['uid'], 'game exists',
        players=json.loads(game['players']),
        rolls=game['rolls'],
        messages=game['messages'],
    )


@router.route('/api/game/join', methods=['POST'])
def _api_game_join():
    data, req_error = check_request(("game_uuid", "username", "uid"))
    if req_error:
        return req_error
    try:
        players = db.query_db(
            'select players from game where uuid = ?', (data['game_uuid'],), one=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    if not players:
        return error(data['uid'], "game doesn't exist")
    players = json.loads(players['players'])
    players['players'].routerend(data['username'])
    try:
        db.query_db(
            'update game set players = ? where uuid = ?', (json.dumps(players), data['game_uuid']), commit=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], 'game exists')
