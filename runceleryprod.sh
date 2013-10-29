#!/bin/bash
python runcelery.py prod worker -l info --time-limit=300
