#!/usr/bin/env python3

from my_jdr import create_app, db
from my_jdr.game.functions import generate_lobby_code, generate_game_code, generate_rolls, generate_rolls_uid
import sqlite3
import json
from flask import request

app = create_app()
port = 5000


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


@app.route('/api/new_user', methods=['POST'])
def _api_new_user():
    data, req_error = check_request(("username", "password", 'uid'))
    if req_error:
        return req_error
    query = 'insert into user (username, password) values(?, ?)'
    try:
        db.query_db(query, (data['username'], data['password']), commit=True)
    except sqlite3.IntegrityError as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'], "Username already taken")
    return success(data['uid'], "created user successfully", 201)


# @app.route('/api/users', methods=['POST'])
# def _api_users():
#     # query = 'insert into user values (0, "ngpyro", "ngpyro")'
#     # data: list[sqlite3.Row] = db.query_db(query)
#     # print("Data:", data)
#     query = 'SELECT * FROM user'
#     data: list[sqlite3.Row] = db.query_db(query)
#     datum: sqlite3.Row
#     body = {}
#     for i, datum in enumerate(data):
#         body[i] = {'id': datum["id"], 'username': datum["username"],
#                    'password': datum["password"]}
#     print(request.data)
#     return json.dumps(body), 200


@app.route('/api/lobby/create', methods=['POST'])
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


@app.route('/api/lobby/delete', methods=['POST'])
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


@app.route('/api/lobby/list_one', methods=['POST'])
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


@app.route('/api/lobby/join', methods=['POST'])
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


@app.route('/api/lobby/start', methods=['POST'])
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


@app.route('/api/game/list_one', methods=['POST'])
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


@app.route('/api/game/join', methods=['POST'])
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
    players['players'].append(data['username'])
    try:
        db.query_db(
            'update game set players = ? where uuid = ?', (json.dumps(players), data['game_uuid']), commit=True)
    except Exception as e:
        print(f'Request failed because: {str(e)}')
        return error(data['uid'])
    return success(data['uid'], 'game exists')


@app.route('/api/dice/throw', methods=['POST'])
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
