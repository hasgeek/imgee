# -*- coding: utf-8 -*-

from functools import wraps

from flask import Response, redirect, flash, g, url_for, request, abort
from flask.ext.lastuser.sqlalchemy import UserManager
from coaster.views import get_next_url

from imgee import app, lastuser
from imgee.models import db, User, Profile, PROFILE_TYPE

lastuser.init_usermanager(UserManager(db, User))


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id email organizations'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(u"You are now logged out", category='info')
    return get_next_url()


def make_profiles():
    # Make profiles for the user's organizations
    username = g.user.username or g.user.userid
    profile = Profile.query.filter_by(userid=g.user.userid).first()
    if profile is None:
        profile = Profile(userid=g.user.userid,
            name=g.user.username or g.user.userid,
            title=g.user.fullname,
            type=PROFILE_TYPE.PERSON)
        db.session.add(profile)
    else:
        if profile.name != username:
            profile.name = username
        if profile.title != g.user.fullname:
            profile.title = g.user.fullname
    for org in g.user.organizations_owned():
        profile = Profile.query.filter_by(userid=org['userid']).first()
        if profile is None:
            profile = Profile(userid=org['userid'],
                name=org['name'],
                title=org['title'],
                type=PROFILE_TYPE.ORGANIZATION)
            db.session.add(profile)
        else:
            if profile.name != org['name']:
                profile.name = org['name']
            if profile.title != org['title']:
                profile.title = org['title']
    db.session.commit()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    make_profiles()
    return redirect(get_next_url())


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(get_next_url())
    return Response(u"Error: %s\n"
                    u"Description: %s\n"
                    u"URI: %s" % (error, error_description, error_uri),
                    mimetype="text/plain")
