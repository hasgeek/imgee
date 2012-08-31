from imgee.models import db, User

def create_user(self):
    user = User(username=u'nigelb', userid=u'WzTwFMKEQ5yozIkDj7feCw',
                lastuser_token_scope=u'id', lastuser_token_type=u'bearer',
                lastuser_token=u'-zhQm-NRSRaVfLQnebR3Mw',
                fullname=u'Nigel Babu', id=1)
    db.session.add(user)
    db.session.commit()
    return user
