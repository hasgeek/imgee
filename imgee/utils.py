# -*- coding: utf-8 -*-

from imgee.models import db, Label, Profile

def save_label(label_name, profile_id):
    profile = Profile.query.filter_by(userid=profile_id).one()
    label = Label(name=label_name, profile=profile)
    db.session.add(label)
    db.session.commit()
    return label

def delete_label(label):
    db.session.delete(label)
    db.session.commit()


