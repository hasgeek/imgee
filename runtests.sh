#!/bin/sh
set -e
export FLASK_ENV="TESTING"
./manage.py init  # creates the test upload directory
coverage run `which nosetests` --with-timer "$@"
coverage report -m
