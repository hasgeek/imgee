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

def save_labels_to(stored_file, labels):
    new_labels = [l for l in labels if not l in stored_file.labels]
    if new_labels:
        stored_file.labels.extend(new_labels)
        db.session.commit()
    return new_labels

def remove_labels_from(stored_file, labels):
    # improve this
    to_remove = [l for l in labels if l in stored_file.labels]
    for label in to_remove:
        stored_file.labels.remove(label)
    if to_remove:
        db.session.commit()
    return to_remove
