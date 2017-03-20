from StringIO import StringIO
import requests
import os
from PIL import Image
from imgee.models import StoredFile, db


def upload(test_client, filepath, upload_url):
    filepath = os.path.abspath(filepath)
    filename = os.path.basename(filepath)
    response = None
    with open(filepath) as f:
        content = f.read()
        d = {'file': (StringIO(content), unicode(filename))}
        with test_client.session_transaction() as session:
            session['lastuser_userid'] = test_client.test_user.userid
            session['lastuser_sessionid'] = 'some-session-id'
            response = test_client.post(upload_url, data=d, follow_redirects=False)
            print response.headers
    return filename, response


def get_img_id(img_title):
    img = StoredFile.query.filter_by(title=img_title).order_by('created_at desc').first()
    return img and img.name


def download_image(url):
    r = requests.get(url)
    assert r.status_code == 200
    imgio = StringIO()
    for chunk in r.iter_content(1024):
        imgio.write(chunk)
    imgio.seek(0)
    return imgio


def get_image_size(path):
    img = Image.open(path)
    return img.size


if __name__ == '__main__':
    import doctest
    doctest.testmod()
