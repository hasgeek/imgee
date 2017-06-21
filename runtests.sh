#!/bin/sh
set -e
export FLASK_ENV="TESTING"
export PYTHONPATH=$(dirname $0)  # setting project root as PYTHONPATH
coverage run `which nosetests` "$@"
coverage report -m
