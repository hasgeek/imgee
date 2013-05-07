from bs4 import BeautifulSoup
from StringIO import StringIO
import requests
import os
from PIL import Image

def upload(test_client, filepath, upload_url):
    content = open(filepath).read()
    filename = os.path.basename(filepath)
    d = {'uploaded_file': (StringIO(content), filename)}
    response = test_client.post(upload_url, data=d, follow_redirects=True)
    return filename, response

def get_img_id(r, img_title):
    """
    >>> r = r'''<div class="image">
    ... <span class="delete"><a href="/delete/abcd">X</a></span>
    ... <a href="/asldevi/view/abcd">
    ...     <img src="/thumbnail/abcd"/>
    ... </a>
    ... <div class="title">earth_moon_4test.gif</div>
    ... <div class="labels">
    ... </div>'''
    ...
    >>> get_img_id(r, 'earth_moon_4test.gif')
    u'abcd'
    """
    soup = BeautifulSoup(r)
    img_div = soup.find(text=img_title).findParent('div', attrs={'class': 'image'})
    x = img_div.find('a')['href']
    return x.split('/')[-1]


def get_image_count(html):
    soup = BeautifulSoup(html)
    imgs = soup.findAll('div', attrs={'class': 'image'})
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
