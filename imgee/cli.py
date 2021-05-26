import os
from . import app


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


@app.cli.command('init')
def init():
    mkdir_p(app.upload_folder)
