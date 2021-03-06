# coding: utf-8
#
# This file is part of Supysonic.
# Supysonic is a Python implementation of the Subsonic server API.
#
# Copyright (C) 2013-2018 Alban 'spl0k' Féron
#
# Distributed under terms of the GNU AGPLv3 license.

from flask import request
from functools import wraps

from ..db import User
from ..managers.user import UserManager
from ..py23 import dict

from . import api, decode_password
from .exceptions import Forbidden, GenericError, NotFound

def admin_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.user.admin:
            raise Forbidden()
        return f(*args, **kwargs)
    return decorated

@api.route('/getUser.view', methods = [ 'GET', 'POST' ])
def user_info():
    username = request.values['username']

    if username != request.user.name and not request.user.admin:
        raise Forbidden()

    user = User.get(name = username)
    if user is None:
        raise NotFound('User')

    return request.formatter('user', user.as_subsonic_user())

@api.route('/getUsers.view', methods = [ 'GET', 'POST' ])
@admin_only
def users_info():
    return request.formatter('users', dict(user = [ u.as_subsonic_user() for u in User.select() ] ))

@api.route('/createUser.view', methods = [ 'GET', 'POST' ])
@admin_only
def user_add():
    username = request.values['username']
    password = request.values['password']
    email = request.values['email']
    admin = request.values.get('adminRole')
    admin = True if admin in (True, 'True', 'true', 1, '1') else False

    password = decode_password(password)
    UserManager.add(username, password, email, admin)

    return request.formatter.empty

@api.route('/deleteUser.view', methods = [ 'GET', 'POST' ])
@admin_only
def user_del():
    username = request.values['username']
    UserManager.delete_by_name(username)

    return request.formatter.empty

@api.route('/changePassword.view', methods = [ 'GET', 'POST' ])
def user_changepass():
    username = request.values['username']
    password = request.values['password']

    if username != request.user.name and not request.user.admin:
        raise Forbidden()

    password = decode_password(password)
    UserManager.change_password2(username, password)

    return request.formatter.empty

