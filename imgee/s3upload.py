import os
import time

from imgee import app
from imgee.storage import save_on_s3, s3uploadqueue

def upload_images_on_s3(queue):
    queue.connect()
    while True:
        task = queue.wait()
        img_name = task.data['name']
        path = os.path.join(app.config['UPLOADED_FILES_DEST'], img_name)
        with open(path) as img:
            try:
                save_on_s3(img, img_name)
            except:
                queue.add(img_name)
                time.sleep(60)


if __name__ == '__main__':
    from imgee import init_for
    from imgee.utils import ImageQueue

    init_for('dev')
    q = ImageQueue()
    q.add('logo.gif')
    upload_images_on_s3(q)