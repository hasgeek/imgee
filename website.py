import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from imgee import app as application, init_for
init_for(os.getenv('ENV', 'production'))
