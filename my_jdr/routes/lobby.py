#!/usr/bin/env python3

from flask import Blueprint

router = Blueprint('lobby', __name__)

@router.route('/lobby/list_all')
def lobby_list_all():
    pass
