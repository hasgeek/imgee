from flask import render_template, Flask
from baseframe.forms.fields import ImgeeField
from flask.ext.wtf import Form
from wtforms.validators import Required
from baseframe import baseframe

app = Flask(__name__)

imgee_url = app.config.get('IMGEE_ENDPOINT', 'http://0.0.0.0:4500')

app.config['SECRET_KEY'] = 'not set'

class ImgeeForm(Form):
    image = ImgeeField(label='Logo', description='Your company logo here',
           validators=[Required()],
           profile='asldevi', img_label='', img_size='100x75'
    )


@app.route('/')
def index():
    form = ImgeeForm()
    return render_template('index.html', form=form, imgee_url=imgee_url)


def init_for(env):
    baseframe.init_app(app, requires=['baseframe'])

if __name__ == "__main__":
    init_for('dev')
    app.run(port=4333, debug=True)

