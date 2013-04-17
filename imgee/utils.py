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

def save_label_to(stored_file, label):
    if label not in stored_file.labels:
        stored_file.labels.append(label)
        db.session.commit()
        return True
    return False

def remove_label_from(stored_file, label):
    if label in stored_file.labels:
        stored_file.labels.remove(label)
        db.session.commit()
        return True
    return False
