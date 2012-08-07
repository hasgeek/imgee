#!/usr/bin/env python
from imgee import app, init_for
from imgee.models import db
init_for('dev')
db.create_all()
app.run('0.0.0.0', debug=True, port=4500)
