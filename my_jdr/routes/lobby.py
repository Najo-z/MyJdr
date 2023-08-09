#!/usr/bin/env python3

from flask import Blueprint
import sqlite3
from .. import db
import json
from ..game.functions import generate_game_code, generate_lobby_code
from .util import error, success, check_request

router = Blueprint('lobby', __name__)


@router.route('/api/lobby/list_all', methods=['GET', 'POST'])
def lobby_list_all():
    return {"ok": "ok"}, 400


@router.route('/api/lobby/create', methods=['POST'])
def _api_lobby_create():
    data, req_error = check_request(("username", "uid",))
    if req_error:
        return req_error
    try:
        in_use = [v['code'] for v in db.query_db('select * from lobby')]
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    lobby_code = generate_lobby_code(in_use)
    players = {
        'game_master': data['username'],
        'players': [],
    }
    query = 'insert into lobby (code, players, started, game_code) values(?, ?, 0, -1)'
    try:
        db.query_db(query, (lobby_code, json.dumps(players)), commit=True)
    except sqlite3.IntegrityError as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], "created lobby successfully", 201, lobby_code=lobby_code)


@router.route('/api/lobby/delete', methods=['POST'])
def _api_lobby_delete():
    data, req_error = check_request(("lobby_code", 'uid'))
    if req_error:
        return req_error
    query = 'delete from lobby where code=?'
    try:
        db.query_db(query, (data['lobby_code'],), commit=True)
    except sqlite3.IntegrityError as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], "deleted lobby successfully", 201)


@router.route('/api/lobby/list_one', methods=['POST'])
def _api_lobby_list_one():
    data, req_error = check_request(("lobby_code", 'uid'))
    if req_error:
        return req_error
    try:
        lobby = db.query_db(
            'select * from lobby where code = ?', (data['lobby_code'],), one=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    if not lobby:
        return error(data['uid'], "lobby doesn't exist")
    return success(
        data['uid'], 'lobby exists',
        players=json.loads(lobby['players']),
        started=lobby['started'],
        game_code=lobby['game_code'],
    )


@router.route('/api/lobby/join', methods=['POST'])
def _api_lobby_join():
    data, req_error = check_request(("lobby_code", "username", "uid"))
    if req_error:
        return req_error
    try:
        players = db.query_db(
            'select players from lobby where code = ?', (data['lobby_code'],), one=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    if not players:
        return error(data['uid'], "lobby doesn't exist")
    players = json.loads(players['players'])
    players['players'].append(data['username'])
    try:
        db.query_db(
            'update lobby set players = ? where code = ?', (json.dumps(players), data['lobby_code']), commit=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], 'lobby exists')


@router.route('/api/lobby/start', methods=['POST'])
def _api_lobby_start():
    data, req_error = check_request(("lobby_code", "uid"))
    if req_error:
        return req_error
    try:
        lobby = db.query_db(
            'select * from lobby where code = ?', (data['lobby_code'],), one=True)
        if not lobby:
            return error(data['uid'], "lobby doesn't exist")
        new_players = json.loads(lobby['players'])
        new_players['players'] = []
        game_code = generate_game_code()
        db.query_db(
            'insert into game (uuid, players, rolls, messages) values(?, ?, ?, ?)',
            (
                str(game_code),
                json.dumps(new_players),
                json.dumps({'rolls': []}),
                json.dumps({'messages': []}),
            ),
            commit=True,
        )
        db.query_db(
            'update lobby set started = ?, game_code = ? where code = ?', (True, str(game_code), data['lobby_code']), commit=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], 'lobby exists', game_code=str(game_code))
