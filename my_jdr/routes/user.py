#!/usr/bin/env python3

from flask import Blueprint
from .. import db
import sqlite3
from .util import error, success, check_request

router = Blueprint('user', __name__)


@router.route('/api/new_user', methods=['POST'])
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
