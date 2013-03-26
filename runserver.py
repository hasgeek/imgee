#!/usr/bin/env python
from imgee import app, init_for
from imgee.models import db
db.create_all()
init_for('dev')
app.run('0.0.0.0', debug=True, port=4500)
