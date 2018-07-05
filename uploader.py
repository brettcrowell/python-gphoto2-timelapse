import boto3
import os


class Uploader:
    def upload(self, image_path, image_meta):
        raise NotImplementedError


class S3BucketUploader(Uploader):
    def __init__(self):
        self.bucket_name = os.environ.get('TIMELAPSE_BUCKET', "bc-timelapse")
        self.client = boto3.client('s3')

    def upload(self, image_path, image_meta, retries = 2):

        try:

            filename = "{}/{}.jpg".format(image_meta['name'], image_meta['ts'])

            self.client.upload_file(image_path, self.bucket_name, filename)

            os.remove(image_path)

        except:

            if retries > 0:
                # keep retrying until the upload succeeds
                self.upload(image_path, image_meta, retries - 1)

            else:
                # give up and leave the file on disk
                return None
