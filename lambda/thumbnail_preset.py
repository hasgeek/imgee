from __future__ import print_function
import boto3
import os
from PIL import Image
import mimetypes
import subprocess

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')


class ThumbnailGenerator(object):
    """
    Downloads image from s3,
    then generates and uploads thumbnails back to s3
    """

    SIZES = {
        'Tiny': (75, 75),
        'Avatar': (150, 150),
        'Thumbnail': (100, 75),
        'Small': (320, 240),
        'Medium': (640, 480),
        'Large': (1024, 768)
    }

    DOWNLOAD_DIR = "/tmp"
    THUMB_EXTN = "jpg"
    S3_THUMB_DIR = "thumb"

    IMAGE_MIMETYPES = [
        'image/jpg', 'image/jpe', 'image/jpeg', 'image/pjpeg', 'image/png',
        'image/gif', 'image/bmp', 'image/x-bmp', 'image/x-bitmap',
        'image/x-xbitmap', 'image/x-win-bitmap', 'image/x-windows-bmp',
        'image/ms-bmp', 'image/x-ms-bmp', 'application/bmp',
        'application/x-bmp', 'application/x-win-bitmap'
    ]

    # image extensions that Pillow can handle
    IMAGE_EXTENSION = [
        '.jpe', '.jpg', '.jpeg', '.png', '.gif', '.bmp'
    ]

    def __init__(self, key, bucket):
        """
        key - key of the file that was uploaded on s3
        bucket - the Bucket objects from the s3 resource
        """
        self.key = key
        self.bucket = bucket

    def split_key(self, key):
        """
        the source key looks like this - original/randomfilename.ext
        """
        folder, filename_with_ext = os.path.split(key)
        filename, ext = os.path.basename(filename_with_ext)
        return (folder, filename, ext)

    def resize_image(self, image_path, resize_path, size):
        with Image.open(image_path) as image:
            image.thumbnail(size)
            image.save(resize_path)

    def get_thumb_name(self, filename, ext, size):
        w, h = size
        return "{name}_w{w}_h{h}{ext}".format(name=filename, w=w, h=h, ext=ext)

    def get_mimetype(self, filepath):
        mimetype, encoding = mimetypes.guess_type(filepath)
        return mimetype

    def create_image(self, filepath):
        """
        create an image version of the file
        and replace original file with it
        """
        returncode = subprocess.call([
            "convert", filepath, "{}:{}".format(self.THUMB_EXTN, filepath)
        ])

        if returncode != 0:
            raise Exception("Return Code {}: Could not convert '{}' to an image".format(str(returncode), self.key))

    def upload_thumbnail(self, thumb_name):
        resize_path = os.path.join(self.DOWNLOAD_DIR, thumb_name)
        destination_key = os.path.join(self.S3_THUMB_DIR, thumb_name)
        mimetype = self.get_mimetype(resize_path)

        with open(resize_path) as fp:
            self.bucket.put_object(
                ACL='public-read',
                Body=fp,
                CacheControl='max-age=31536000',  # 60*60*24*365
                ContentType=mimetype,
                Key=destination_key
            )

    def create_thumbnail(self, filepath):
        folder, filename, ext = self.split_key(self.key)

        for size in self.SIZES.values():
            thumb_name = self.get_thumb_name(filename, ext, size)
            resize_path = os.path.join(self.DOWNLOAD_DIR, thumb_name)
            self.resize_image(filepath, resize_path)
            self.upload_thumbnail(thumb_name)

    def create_thumbnails(self):
        is_image = True
        folder, filename, ext = self.split_key(self.key)

        download_path = os.path.join(self.DOWNLOAD_DIR, filename)
        s3_client.download_file(self.bucket.name, self.key, download_path)
        mimetype = self.get_mimetype(download_path)

        if ext not in self.IMAGE_EXTENSION and mimetype not in self.IMAGE_MIMETYPES:
            is_image = False

        if is_image:
            self.create_thumbnail(download_path)
        else:
            self.create_image(download_path)
            self.create_thumbnail(download_path)


def handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        bucket = s3_resource.Bucket(bucket_name)
        key = record['s3']['object']['key']

        thumb_generator = ThumbnailGenerator(key, bucket)
        thumb_generator.create_thumbnails()
