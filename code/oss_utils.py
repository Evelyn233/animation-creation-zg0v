# -*- coding: utf-8 -*-
import oss2
import os

endpoint = os.environ['OSS_ENDPOINT']
auth = oss2.StsAuth(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
                    os.environ['ALIBABA_CLOUD_SECURITY_TOKEN'])
bucket = oss2.Bucket(auth, endpoint, os.environ['OSS_BUCKET'])


def upload(object_name, local_filename):
    with open(local_filename, 'rb') as file:
        bucket.put_object(object_name, file)
    return bucket.sign_url('GET', object_name, 3600)


def upload_stream(object_name, stream):
    bucket.put_object(object_name, stream)
    return bucket.sign_url('GET', object_name, 3600)


def upload_local(object_name, local_file_path):
    bucket.put_object_from_file(object_name, local_file_path)
    return bucket.sign_url('GET', object_name, 3600)
