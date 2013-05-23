from flask import render_template, Flask

app = Flask(__name__)

imgee_url = app.config.get('IMGEE_ENDPOINT')

@app.route('/')
def index():
    return render_template('index.html', imgee_url=imgee_url)

if __name__ == "__main__":
    app.run(port=4333, debug=True)

