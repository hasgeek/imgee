from flask import Flask, render_template
from wtforms.validators import Required

from flask_wtf import Form

from baseframe import baseframe
from baseframe.forms.fields import ImgeeField

app = Flask(__name__)

imgee_url = app.config.get('IMGEE_ENDPOINT', 'http://0.0.0.0:4500')

app.config['SECRET_KEY'] = 'not set'


class ImgeeForm(Form):
    image = ImgeeField(
        label='Logo',
        description='Your company logo here',
        validators=[Required()],
        profile='asldevi',
        img_label='',
        img_size='100x75',
    )


@app.route('/')
def index():
    form = ImgeeForm()
    return render_template('index.html.jinja2', form=form, imgee_url=imgee_url)


def init_for(env):
    baseframe.init_app(app, requires=['baseframe'])


if __name__ == "__main__":
    init_for('dev')
    app.run(port=4333, debug=True)
