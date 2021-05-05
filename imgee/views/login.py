from flask import Response, flash, redirect

from baseframe import _
from coaster.auth import current_auth
from coaster.views import get_next_url

from .. import app, lastuser
from ..models import Profile, db


@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id organizations'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash(_("You are now logged out", category='info'))
    return get_next_url()


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    Profile.update_from_user(current_auth.user, db.session)
    db.session.commit()
    return redirect(get_next_url())


@app.route('/login/notify', methods=['POST'])
@lastuser.notification_handler
def lastusernotify(user):
    Profile.update_from_user(user, db.session)
    db.session.commit()


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash(_("You denied the request to login", category='error'))
        return redirect(get_next_url())
    return Response(
        "Error: %s\n"
        "Description: %s\n"
        "URI: %s" % (error, error_description, error_uri),
        mimetype="text/plain",
    )
