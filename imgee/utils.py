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

def get_label_changes(nlabels, olabels):
    if (nlabels == olabels):
        status, diff = '0', []
    elif (nlabels > olabels):
        status, diff = '+', nlabels-olabels
    elif (olabels > nlabels):
        status, diff = '-', olabels-nlabels
    else:
        status, diff = '', nlabels
    return status, list(diff)

def save_labels_to(stored_file, labels):
    new_labels = set(labels)
    old_lables = set(stored_file.labels)
    if new_labels != old_lables:
        stored_file.labels = labels
        db.session.commit()
    return get_label_changes(new_labels, old_lables)