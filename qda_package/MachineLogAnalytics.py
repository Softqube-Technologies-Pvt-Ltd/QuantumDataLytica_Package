import logging
import boto3
from botocore.exceptions import NoCredentialsError
from .MyConfig import get_bucket_name, get_access_key_id, get_secret_access_key


def start_logging(file_path, name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter('[%(asctime)s][%(name)s][Line %(lineno)d]'
                                         '[%(levelname)s]:%(message)s')

    file_handler = logging.FileHandler(file_path, mode='w')

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logger_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logger_formatter)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def stop_logging(logger):
    for handler in logger.handlers:
        handler.close()


def upload_file_to_s3(local_file_path, file_name, workflow):
    bucket_name = get_bucket_name()
    access_key_id = get_access_key_id()
    secret_access_key = get_secret_access_key()
    acl = 'public-read'

    print(f"{local_file_path} file uploading into bucket.")
    # Create an S3 client with explicit credentials
    s3 = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    s3_file_name = f"{workflow}/{file_name}"
    try:
        # Upload the file
        s3.upload_file(local_file_path, bucket_name, s3_file_name, ExtraArgs={'ACL': acl, 'ContentType': 'text/plain'})
        print(f'Successfully uploaded {local_file_path} to {bucket_name}/{s3_file_name}')
    except NoCredentialsError:
        print('Credentials not available or not valid.')
