from bs4 import BeautifulSoup
from StringIO import StringIO
import requests
import os
from PIL import Image
from imgee.models import StoredFile

def upload(test_client, filepath, upload_url):
    content = open(filepath).read()
    filename = os.path.basename(filepath)
    d = {'uploaded_file': (StringIO(content), filename)}
    response = test_client.post(upload_url, data=d, follow_redirects=True)
    return filename, response


def get_img_id(r, img_title):
    img = StoredFile.query.filter_by(title=img_title).first()
    return img and img.name

def get_image_count(html):
    soup = BeautifulSoup(html)
    imgs = soup.findAll('li', attrs={'class': 'image'})
    return len(imgs)


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
