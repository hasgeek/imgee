#!/bin/sh
set -e
export FLASK_ENV="TESTING"
export PYTHONPATH=$(pwd)  # setting project root as PYTHONPATH
./manage.py init  # creates the test upload directory
coverage run `which nosetests` "$@"
coverage report -m
